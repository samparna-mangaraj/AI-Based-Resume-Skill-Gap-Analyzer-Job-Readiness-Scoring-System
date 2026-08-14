// ============================================
// SKILL GAP ANALYZER ENGINE
// ============================================
// Core matching logic with weighted scoring,
// synonym resolution, and multi-role comparison.

const SkillAnalyzer = (() => {

  // ── Weights ──
  const WEIGHTS = {
    core: 0.6,
    secondary: 0.3,
    bonus: 0.1
  };

  // ── Match Level Thresholds ──
  const MATCH_LEVELS = [
    { min: 90, max: 100, level: "Excellent", color: "#00ff88", emoji: "🏆" },
    { min: 75, max: 89,  level: "Strong",    color: "#00f5ff", emoji: "💪" },
    { min: 60, max: 74,  level: "Moderate",  color: "#0080ff", emoji: "📈" },
    { min: 40, max: 59,  level: "Beginner",  color: "#ff6b00", emoji: "🌱" },
    { min: 0,  max: 39,  level: "Poor Fit",  color: "#ff4444", emoji: "⚠️" }
  ];

  // ── Normalize a single skill ──
  function normalizeSkill(skill) {
    if (!skill) return "";
    let normalized = skill.toLowerCase().trim();
    
    // Remove common prefixes/suffixes like .js, .py, etc. for better matching
    const cleanNormalized = normalized.replace(/\.(js|py|rb|ts|cpp|csharp|net)$/, "");
    
    if (window.SKILL_SYNONYMS) {
      if (window.SKILL_SYNONYMS[normalized]) {
        normalized = window.SKILL_SYNONYMS[normalized];
      } else if (window.SKILL_SYNONYMS[cleanNormalized]) {
        normalized = window.SKILL_SYNONYMS[cleanNormalized];
      }
    }
    return normalized;
  }

  // ── Normalize an array of skills ──
  function normalizeSkills(skills) {
    if (!Array.isArray(skills)) return [];
    return [...new Set(skills.map(normalizeSkill).filter(Boolean))];
  }

  // ── Partial matching support ──
  // Returns 1.0 for exact match, 0.5 for partial match (basic/intermediate keywords), 0 for no match
  function getSkillMatchScore(userSkill, requiredSkill) {
    if (userSkill === requiredSkill) return 1.0;

    // Partial matching: "basic python" → "python" = 0.5
    const partialKeywords = ["basic", "beginner", "intermediate", "intro", "fundamentals", "learning"];
    for (const keyword of partialKeywords) {
      if (userSkill.includes(keyword) && userSkill.includes(requiredSkill)) {
        return 0.5;
      }
      if (userSkill.includes(requiredSkill) || requiredSkill.includes(userSkill)) {
        return 0.75;
      }
    }

    // Substring matching for compound skills
    if (userSkill.includes(requiredSkill) || requiredSkill.includes(userSkill)) {
      return 0.75;
    }

    return 0;
  }

  // ── Calculate match for a tier (core/secondary/bonus) ──
  function calculateTierMatch(userSkills, tierSkills) {
    if (!tierSkills || tierSkills.length === 0) return { percentage: 100, matched: [], missing: [] };

    const matched = [];
    const missing = [];
    let totalScore = 0;

    for (const required of tierSkills) {
      let bestScore = 0;
      let bestMatch = null;

      for (const userSkill of userSkills) {
        const score = getSkillMatchScore(userSkill, required);
        if (score > bestScore) {
          bestScore = score;
          bestMatch = userSkill;
        }
      }

      if (bestScore > 0) {
        totalScore += bestScore;
        matched.push({ skill: required, score: bestScore, matchedWith: bestMatch });
      } else {
        missing.push(required);
      }
    }

    const percentage = (totalScore / tierSkills.length) * 100;

    return { percentage: Math.round(percentage * 100) / 100, matched, missing };
  }

  // ── Calculate overall match for ONE job category ──
  function calculateMatch(userSkills, category, options = {}) {
    const { includeAllRoles = true } = options;
    const normalizedUserSkills = normalizeSkills(userSkills);
    const categoryData = window.JOB_CATEGORIES[category];

    if (!categoryData) {
      return { error: `Category "${category}" not found` };
    }

    const coreMatch    = calculateTierMatch(normalizedUserSkills, categoryData.core);
    const secondaryMatch = calculateTierMatch(normalizedUserSkills, categoryData.secondary);
    const bonusMatch   = calculateTierMatch(normalizedUserSkills, categoryData.bonus);

    // Weighted final score
    const finalScore = Math.round(
      (coreMatch.percentage * WEIGHTS.core) +
      (secondaryMatch.percentage * WEIGHTS.secondary) +
      (bonusMatch.percentage * WEIGHTS.bonus)
    );

    // Clamp to 0-100
    const clampedScore = Math.min(100, Math.max(0, finalScore));

    // Get match level
    const matchLevel = getMatchLevel(clampedScore);

    // Combine all matched and missing skills
    const allMatched = [
      ...coreMatch.matched.map(m => m.skill),
      ...secondaryMatch.matched.map(m => m.skill),
      ...bonusMatch.matched.map(m => m.skill)
    ];

    const allMissing = [
      ...coreMatch.missing,
      ...secondaryMatch.missing,
      ...bonusMatch.missing
    ];

    // Generate recommendations
    const recommendations = generateRecommendations(categoryData, allMissing);

    // Always generate all roles analysis for the ranking section
    const allRoles = includeAllRoles ? analyzeAllRoles(userSkills) : null;

    return {
      category,
      roles: categoryData.roles,
      icon: categoryData.icon,
      color: categoryData.color,
      match_percentage: clampedScore,
      match_level: matchLevel.level,
      match_color: matchLevel.color,
      match_emoji: matchLevel.emoji,
      matched_skills: allMatched,
      missing_skills: allMissing,
      recommendations,
      certifications: categoryData.certifications || [],
      all_roles_analysis: allRoles, // Added for UI rankings
      breakdown: {
        core: {
          percentage: Math.round(coreMatch.percentage),
          matched: coreMatch.matched,
          missing: coreMatch.missing,
          total: categoryData.core.length,
          weight: WEIGHTS.core
        },
        secondary: {
          percentage: Math.round(secondaryMatch.percentage),
          matched: secondaryMatch.matched,
          missing: secondaryMatch.missing,
          total: categoryData.secondary.length,
          weight: WEIGHTS.secondary
        },
        bonus: {
          percentage: Math.round(bonusMatch.percentage),
          matched: bonusMatch.matched,
          missing: bonusMatch.missing,
          total: categoryData.bonus.length,
          weight: WEIGHTS.bonus
        }
      }
    };
  }

  // ── Get match level from score ──
  function getMatchLevel(score) {
    for (const level of MATCH_LEVELS) {
      if (score >= level.min && score <= level.max) {
        return level;
      }
    }
    return MATCH_LEVELS[MATCH_LEVELS.length - 1];
  }

  // ── Generate personalized recommendations ──
  function generateRecommendations(categoryData, missingSkills) {
    const recs = [];
    if (!categoryData.recommendations) return recs;

    // Convert recommendation object to array with priority logic
    const dataRecs = categoryData.recommendations;
    for (const [key, text] of Object.entries(dataRecs)) {
      const isMissing = missingSkills.some(s => 
        s.toLowerCase().includes(key.toLowerCase()) || 
        key.toLowerCase().includes(s.toLowerCase())
      );
      recs.push({
        key: key,
        text: text,
        priority: isMissing ? "high" : "medium"
      });
    }

    // Add generic gaps if not already covered
    missingSkills.forEach(skill => {
      const alreadyCovered = recs.some(r => 
        r.key.toLowerCase().includes(skill.toLowerCase()) || 
        skill.toLowerCase().includes(r.key.toLowerCase())
      );
      if (!alreadyCovered) {
        recs.push({
          key: skill,
          text: `Focus on mastering ${skill} to meet core job requirements.`,
          priority: "high"
        });
      }
    });

    return recs;
  }

    // ── Analyze against ALL job categories ──
  function analyzeAllRoles(userSkills) {
    const results = {};

    for (const category of Object.keys(window.JOB_CATEGORIES)) {
      results[category] = calculateMatch(userSkills, category, { includeAllRoles: false });
    }

    return results;
  }

  // ── Extract skills from raw text ──
  function extractSkillsFromText(text) {
    if (!text) return [];
    const normalizedText = text.toLowerCase();
    const extracted = new Set();
    
    // Check every skill in every category
    for (const data of Object.values(window.JOB_CATEGORIES)) {
      const allPossibleSkills = [...data.core, ...data.secondary, ...data.bonus];
      for (const skill of allPossibleSkills) {
        // Use word boundaries to avoid partial matches like "tan" in "django"
        const regex = new RegExp(`\\b${skill.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\b`, 'i');
        if (regex.test(normalizedText)) {
          extracted.add(skill);
        }
      }
    }

    // Also check synonym map
    if (window.SKILL_SYNONYMS) {
      for (const [abbr, full] of Object.entries(window.SKILL_SYNONYMS)) {
        const regex = new RegExp(`\\b${abbr.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\b`, 'i');
        if (regex.test(normalizedText)) {
          extracted.add(full);
        }
      }
    }

    return Array.from(extracted);
  }

  // ── Find the BEST matching role ──
  function getBestRole(userSkills) {
    const allAnalysis = analyzeAllRoles(userSkills);

    let bestCategory = null;
    let bestScore = -1;

    for (const [category, analysis] of Object.entries(allAnalysis)) {
      if (analysis.match_percentage > bestScore) {
        bestScore = analysis.match_percentage;
        bestCategory = category;
      }
    }

    // Default to first category if none found or all scores are 0
    if (!bestCategory && Object.keys(allAnalysis).length > 0) {
      bestCategory = Object.keys(allAnalysis)[0];
    }

    if (!bestCategory) {
      return { error: "No job categories available for analysis." };
    }

    const best = allAnalysis[bestCategory];

    return {
      best_role: (best.roles && best.roles.length > 0) ? best.roles[0] : "Professional",
      best_category: bestCategory,
      match_percentage: best.match_percentage,
      match_level: best.match_level,
      match_color: best.match_color,
      match_emoji: best.match_emoji,
      matched_skills: best.matched_skills,
      missing_skills: best.missing_skills,
      recommendations: best.recommendations,
      breakdown: best.breakdown,
      all_roles_analysis: allAnalysis
    };
  }

  // ── Analyze Resume vs Job Description (End-to-End Core Matching) ──
  function analyzeAgainstJD(resumeSkillsArr, resumeText, jdText) {
    const extractedFromResume = extractSkillsFromText(resumeText);
    const combinedResumeSkills = [...new Set([...resumeSkillsArr, ...extractedFromResume])];
    
    const jdSkills = extractSkillsFromText(jdText);
    const rSkills = normalizeSkills(combinedResumeSkills);
    const jSkills = normalizeSkills(jdSkills);
    
    const primary = []; 
    const missing = []; 
    const bonus = [];   
    const secondary = []; 
    
    const jSkillsMatched = new Set();
    const rSkillsMatched = new Set();
    
    // Primary: Exact match in both
    jSkills.forEach(req => {
        let foundExact = false;
        rSkills.forEach(res => {
            if (req === res) {
                primary.push(req);
                jSkillsMatched.add(req);
                rSkillsMatched.add(res);
                foundExact = true;
            }
        });
    });
    
    // Secondary: Partial matches
    jSkills.forEach(req => {
        if (jSkillsMatched.has(req)) return;
        let bestPartial = null;
        let maxScore = 0;
        rSkills.forEach(res => {
            if (rSkillsMatched.has(res)) return;
            const score = getSkillMatchScore(res, req);
            if (score > 0 && score > maxScore) {
                maxScore = score;
                bestPartial = res;
            }
        });
        if (bestPartial) {
            secondary.push({ req, res: bestPartial, score: maxScore });
            jSkillsMatched.add(req);
            rSkillsMatched.add(bestPartial);
        } else {
            missing.push(req);
        }
    });

    // Bonus: Remainder in Resume
    rSkills.forEach(res => {
        if (!rSkillsMatched.has(res)) {
            bonus.push(res);
        }
    });
    
    // 📊 MATCH SCORE CALCULATION
    const totalReqSkills = jSkills.length || 1; 
    let skillScore = 0;
    primary.forEach(() => skillScore += 1);
    secondary.forEach(s => skillScore += s.score);
    const rawSkillMatchPct = (skillScore / totalReqSkills) * 100;
    
    // Keyword / Context Match Engine
    const contextKeywords = ['frontend', 'backend', 'api', 'scalable', 'performance', 'agile', 'cloud', 'architecture', 'database', 'optimization', 'testing', 'security', 'ui', 'ux', 'infrastructure', 'algorithms', 'rest', 'graphql'];
    const jdLower = jdText.toLowerCase();
    const rLower = (resumeText + " " + resumeSkillsArr.join(" ")).toLowerCase();
    
    const jdKeywords = contextKeywords.filter(k => jdLower.includes(k));
    const rKeywords = jdKeywords.filter(k => rLower.includes(k));
    
    let contextScorePct = 100;
    if (jdKeywords.length > 0) {
        contextScorePct = (rKeywords.length / jdKeywords.length) * 100;
    }
    
    // Weighted Total Score (70% Skill, 30% Context)
    const finalScore = Math.round((rawSkillMatchPct * 0.70) + (contextScorePct * 0.30));
    const clampedScore = Math.min(100, Math.max(0, finalScore));
    const matchLevel = getMatchLevel(clampedScore);
    
    const certs = generateCertRecommendations(missing, jdText);
    const recs = generateJDRecommendations(missing, jdKeywords, rKeywords);

    let whyExplanation = `Job suitability is determined by a ${Math.round(rawSkillMatchPct)}% exact skill match and a ${Math.round(contextScorePct)}% contextual keyword match. Your resume aligns with ${primary.length} primary required skills exactly and has ${secondary.length} secondary (related) matches out of ${jSkills.length} required skills. `;
    if (contextScorePct < 50 && jdKeywords.length > 0) {
        whyExplanation += `But it lacks key role context words like "${jdKeywords.filter(k => !rKeywords.includes(k)).slice(0,3).join(', ')}" found in the job description, limiting your score.`;
    } else {
        whyExplanation += `Your experience details align beautifully with the job role context!`;
    }
    
    return {
      category: "Job Description Match",
      roles: ["JD Match Output"],
      icon: "🎯",
      color: matchLevel.color,
      match_percentage: clampedScore,
      match_level: matchLevel.level,
      match_color: matchLevel.color,
      match_emoji: matchLevel.emoji,
      primary_skills: primary,
      secondary_skills: secondary.map(s => s.req + ` (Matched: ${s.res})`),
      bonus_skills: bonus,
      missing_skills: missing,
      recommendations: recs,
      certifications: certs,
      why_explanation: whyExplanation,
      mode: "jd_match",
      breakdown: {
         skillMatch: Math.round(rawSkillMatchPct),
         contextMatch: Math.round(contextScorePct)
      }
    };
  }

  function generateCertRecommendations(missing, jdText) {
    const jdLower = jdText.toLowerCase();
    const certs = [];
    if (missing.some(m => m.includes('aws') || m.includes('cloud')) || jdLower.includes('aws')) certs.push({ name: "AWS Certified Solutions Architect", provider: "Amazon Web Services" });
    if (missing.some(m => m.includes('azure')) || jdLower.includes('azure')) certs.push({ name: "Microsoft Certified: Azure Fundamentals", provider: "Microsoft" });
    if (missing.some(m => m.includes('gcp') || m.includes('google')) || jdLower.includes('gcp')) certs.push({ name: "Google Cloud Professional Cloud Architect", provider: "Google" });
    if (missing.some(m => m.includes('react') || m.includes('node') || m.includes('frontend')) || jdLower.includes('frontend')) certs.push({ name: "Meta Front-End Developer Professional Certificate", provider: "Meta / Coursera" });
    if (missing.some(m => m.includes('cyber') || m.includes('security')) || jdLower.includes('security')) certs.push({ name: "CompTIA Security+", provider: "CompTIA" });
    if (missing.some(m => m.includes('sql') || m.includes('data')) || jdLower.includes('database')) certs.push({ name: "Google Data Analytics Professional Certificate", provider: "Google / Coursera" });

    if (certs.length === 0) {
        certs.push({ name: "Relevant Mastery Course", provider: "Udemy" });
        certs.push({ name: "Professional Career Certification", provider: "Coursera" });
    }
    return certs;
  }
  
  function generateJDRecommendations(missing, jdKeys, rKeys) {
      const recs = [];
      missing.slice(0,3).forEach(skill => {
          recs.push({
              key: `Learn and Master ${skill}`,
              text: `Focus on mastering ${skill}. Action: Build 1-2 practical projects demonstrating this skill. Practical tasks: Develop a hands-on application utilizing ${skill}.`,
              priority: "high"
          });
      });
      const missingKeys = jdKeys.filter(k => !rKeys.includes(k));
      missingKeys.slice(0,2).forEach(key => {
           recs.push({
              key: `Highlight Context: ${key.toUpperCase()}`,
              text: `Your resume lacks contextual experience in "${key}". Action: If you have this experience, reword your resume bullets to naturally include keywords indicating you have worked with scalable, performance-optimized, or relevant systems.`,
              priority: "medium"
          });
      });
      if(recs.length === 0){
           recs.push({
              key: "Polish & Apply",
              text: "You have an excellent match! Action: Focus on polishing your interview skills and preparing to discuss your robust experience level.",
              priority: "medium"
          });
      }
      return recs;
  }

  // ── Public API ──
  return {
    normalizeSkills,
    normalizeSkill,
    calculateMatch,
    analyzeAllRoles,
    extractSkillsFromText,
    getBestRole,
    getMatchLevel,
    analyzeAgainstJD,
    WEIGHTS,
    MATCH_LEVELS
  };

})();

// Expose to global scope for frontend use
if (typeof window !== 'undefined') {
  window.SkillAnalyzer = SkillAnalyzer;
}