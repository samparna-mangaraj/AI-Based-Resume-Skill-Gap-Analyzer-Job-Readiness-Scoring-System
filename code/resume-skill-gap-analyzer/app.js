/**
 * MAIN APP MODULE — SkillGap Analyzer
 * ──────────────────────────────────────────
 * Handles UI interactions for Dashboard & Results
 */

const SGA = (() => {

    // ── CONFIG ─────────────────────────────────────
    const API_BASE_URL = (window.location.origin && window.location.origin !== 'null' && window.location.protocol !== 'file:') 
        ? window.location.origin + '/api/v1' 
        : 'http://localhost:8000/api/v1';

    // Safe Storage Helper
    const storage = {
        get: (key) => {
            try { return localStorage.getItem(key); } catch (e) { return null; }
        },
        set: (key, val) => {
            try { localStorage.setItem(key, val); return true; } catch (e) { return false; }
        },
        remove: (key) => {
            try { localStorage.removeItem(key); return true; } catch (e) { return false; }
        }
    };

    // ── STATE ──────────────────────────────────────
    const state = {
        skills: new Set(),
        category: null,
        resumeText: null,
        jdText: null
    };

    // ── ELEMENTS ───────────────────────────────────
    const elements = {
        skillsInput: document.getElementById('skills-input'),
        tagsContainer: document.getElementById('live-tags'),
        categoryDropdown: document.getElementById('category-dropdown'),
        analyzeBtn: document.getElementById('analyze-btn'),
        hintsSection: document.getElementById('hints-section'),
        hintsGrid: document.getElementById('hints-grid'),
        resumeUpload: document.getElementById('resume-upload'),
        jdUpload: document.getElementById('jd-upload'),
        uploadZone: document.getElementById('upload-zone'),
        jdUploadZone: document.getElementById('jd-upload-zone')
    };

    // ── INITIALIZATION ────────────────────────────
    function init() {
        checkBackendStatus();
        initAuth();
        if (elements.skillsInput) setupDashboard();
    }

    async function checkBackendStatus() {
        const statusEl = document.getElementById('backend-status');
        if (!statusEl) return;

        try {
            const res = await fetch(`${API_BASE_URL.replace('/api/v1', '')}/health`);
            if (res.ok) {
                statusEl.style.background = 'rgba(0, 245, 255, 0.1)';
                statusEl.style.color = '#00f5ff';
                statusEl.style.borderColor = 'rgba(0, 245, 255, 0.2)';
                const dotSize = statusEl.style.fontSize === '11px' ? '6px' : '8px';
                statusEl.innerHTML = `<span style="width: ${dotSize}; height: ${dotSize}; border-radius: 50%; background: #00f5ff; display: inline-block;"></span> Backend Online`;
            }
        } catch (e) {
            // Keep default offline style
        }
    }

    // ── DASHBOARD LOGIC ───────────────────────────
    function setupDashboard() {
        // 1. Populate Categories
        if (window.JOB_CATEGORIES) {
            Object.keys(window.JOB_CATEGORIES).forEach(cat => {
                const opt = document.createElement('option');
                opt.value = cat;
                opt.textContent = cat;
                elements.categoryDropdown.appendChild(opt);
            });
        }

        // 2. Events
        elements.skillsInput.addEventListener('input', handleManualInput);
        elements.categoryDropdown.addEventListener('change', (e) => {
            state.category = e.target.value;
            updateAnalyzeState();
            showHints(state.category);
        });

        elements.analyzeBtn.addEventListener('click', runAnalysis);
        
        document.getElementById('demo-fill-btn')?.addEventListener('click', fillDemo);
        document.getElementById('clear-skills-btn')?.addEventListener('click', clearAll);

        // 3. File Uploads
        elements.resumeUpload?.addEventListener('change', (e) => handleFileUpload(e, 'resume'));
        elements.jdUpload?.addEventListener('change', (e) => handleFileUpload(e, 'jd'));
    }

    function handleManualInput() {
        const text = elements.skillsInput.value;
        if (text.includes(',')) {
            const parts = text.split(',');
            elements.skillsInput.value = parts.pop().trim();
            parts.forEach(p => addSkill(p.trim()));
        }
        updateAnalyzeState();
    }

    function addSkill(skill) {
        if (!skill) return;
        const normalized = SkillAnalyzer.normalizeSkill(skill);
        if (!state.skills.has(normalized)) {
            state.skills.add(normalized);
            renderTags();
        }
    }

    function removeSkill(skill) {
        state.skills.delete(skill);
        renderTags();
        updateAnalyzeState();
    }

    function renderTags() {
        elements.tagsContainer.innerHTML = '';
        state.skills.forEach(skill => {
            const tag = document.createElement('span');
            tag.className = 'live-tag';
            tag.innerHTML = `${skill} <button>&times;</button>`;
            tag.querySelector('button').onclick = () => removeSkill(skill);
            elements.tagsContainer.appendChild(tag);
        });
        updateAnalyzeState();
    }

    function updateAnalyzeState() {
        const hasSkills = state.skills.size > 0 || state.resumeText;
        const hasCategory = state.category !== "" && state.category !== null;
        elements.analyzeBtn.disabled = !(hasSkills && hasCategory);
    }

    function showHints(cat) {
        if (cat === 'auto' || !window.JOB_CATEGORIES[cat]) {
            elements.hintsSection.classList.add('hidden');
            return;
        }

        elements.hintsSection.classList.remove('hidden');
        elements.hintsGrid.innerHTML = '';
        const data = window.JOB_CATEGORIES[cat];

        const tiers = [
            { id: 'core', list: data.core },
            { id: 'secondary', list: data.secondary },
            { id: 'bonus', list: data.bonus }
        ];

        tiers.forEach(tier => {
            tier.list.forEach(skill => {
                const chip = document.createElement('div');
                chip.className = `hint-chip tier-${tier.id}`;
                chip.textContent = skill;
                chip.onclick = () => addSkill(skill);
                elements.hintsGrid.appendChild(chip);
            });
        });
    }

    async function handleFileUpload(event, type) {
        const file = event.target.files[0];
        if (!file) return;

        const loadingId = type === 'resume' ? 'upload-loading' : 'jd-upload-loading';
        const successId = type === 'resume' ? 'upload-success' : 'jd-upload-success';
        const zoneId = type === 'resume' ? 'upload-zone' : 'jd-upload-zone';

        const zone = document.getElementById(zoneId);
        const loading = document.getElementById(loadingId);
        const success = document.getElementById(successId);
        const uploadContent = zone.querySelector('.upload-content');

        uploadContent.style.display = 'none';
        loading.style.display = 'flex';

        const formData = new FormData();
        formData.append('resume', file);

        try {
            const token = storage.get('sga_token') || "";
            const res = await fetch(`${API_BASE_URL}/resume/upload`, {
                method: 'POST',
                headers: token ? { 'Authorization': `Bearer ${token}` } : {},
                body: formData
            });

            if (!res.ok) {
                const errData = await res.json();
                throw new Error(errData.detail || "Failed to upload file");
            }

            const data = await res.json();
            
            if (type === 'resume') {
                if (data.extracted_skills && data.extracted_skills.length) {
                    data.extracted_skills.forEach(s => addSkill(s));
                } else if (data.content) {
                   // Fallback extracted text parser using window.JOB_CATEGORIES
                   let allKnown = [];
                   if (window.JOB_CATEGORIES) {
                       Object.values(window.JOB_CATEGORIES).forEach(c => {
                           if(c.core) allKnown = allKnown.concat(c.core);
                           if(c.secondary) allKnown = allKnown.concat(c.secondary);
                           if(c.bonus) allKnown = allKnown.concat(c.bonus);
                       });
                   }
                   const uniqueKnown = [...new Set(allKnown.map(s => s.toLowerCase()))];
                   const textLower = data.content.toLowerCase();
                   uniqueKnown.forEach(s => {
                       // Simple context boundary check
                       const regex = new RegExp(`\\b${s.replace(/[.*+?^\${}()|[\\]\\\\]/g, '\\\\$&')}\\b`, 'i');
                       if (regex.test(data.content)) {
                           const orig = allKnown.find(origStr => origStr.toLowerCase() === s);
                           if(orig) addSkill(orig);
                       }
                   });
                }
                state.resumeText = data.content || "";
                
                // Nudge state category to 'auto' so the analyzer button unlocks if they haven't picked a category
                if (!state.category || state.category === "") {
                    state.category = 'auto';
                    elements.categoryDropdown.value = 'auto';
                }

                const sucMsg = document.getElementById('uploaded-filename');
                if (sucMsg) sucMsg.textContent = data.filename + " Extracted!";
            } else {
                state.jdText = data.content || "";
                
                elements.categoryDropdown.innerHTML = '<option value="jd" selected>Job Description Match</option>';
                elements.categoryDropdown.disabled = true;
                state.category = 'jd';
                
                const jdSucMsg = document.querySelector(`#${successId} p`);
                if (jdSucMsg) jdSucMsg.textContent = data.filename + " Loaded!";
            }

            loading.style.display = 'none';
            success.style.display = 'flex';
            updateAnalyzeState();
        } catch (err) {
            console.error(err);
            loading.style.display = 'none';
            uploadContent.style.display = 'flex';
            alert("File upload failed: " + err.message);
        }
    }

    function fillDemo() {
        const demo = ["node.js", "react", "mongodb", "aws", "docker"];
        demo.forEach(s => addSkill(s));
    }

    function clearAll() {
        state.skills.clear();
        renderTags();
        state.resumeText = null;
        updateAnalyzeState();
    }

    function runAnalysis() {
        const skillsArray = Array.from(state.skills);
        let result;

        if (state.jdText && state.jdText.trim() !== "") {
            const resumeFullText = (state.resumeText || "") + " " + skillsArray.join(", ");
            result = SkillAnalyzer.analyzeAgainstJD(skillsArray, resumeFullText, state.jdText);
        } else {
            if (state.category === 'auto') {
                result = SkillAnalyzer.getBestRole(skillsArray);
            } else {
                result = SkillAnalyzer.calculateMatch(skillsArray, state.category);
            }
        }

        if (result && result.error) {
            alert("Analysis Error: " + result.error);
            return;
        }

        storage.set('sga_result', JSON.stringify(result));
        window.location.href = 'result.html';
    }

    // ── RESULTS RENDERER ──────────────────────────
    function initResultPage() {
        const raw = storage.get('sga_result');
        if (!raw) {
            window.location.href = 'dashboard.html';
            return;
        }

        const data = JSON.parse(raw);
        
        // 1. Basic Info
        const catEl = document.getElementById('result-category');
        const roleEl = document.getElementById('result-role');
        const scoreEl = document.getElementById('score-value');
        const levelEl = document.getElementById('score-level');
        const circle = document.getElementById('score-circle');

        if (catEl) catEl.textContent = data.category || "Skill Analysis";
        if (roleEl) roleEl.textContent = data.roles ? data.roles[0] : (data.best_role || "Professional");
        if (scoreEl) scoreEl.textContent = `${data.match_percentage}%`;
        if (levelEl) {
            levelEl.textContent = data.match_level;
            levelEl.style.color = data.match_color;
        }
        
        if (circle) circle.style.background = `conic-gradient(${data.match_color} ${data.match_percentage * 3.6}deg, var(--bg-tertiary) 0deg)`;

        // 2. Stats
        const statM = document.getElementById('stat-matched');
        const statMi = document.getElementById('stat-missing');
        const statR = document.getElementById('stat-recs');

        if (statM) statM.textContent = data.matched_skills?.length || 0;
        if (statMi) statMi.textContent = data.missing_skills?.length || 0;
        if (statR) statR.textContent = data.recommendations?.length || 0;

        // 3. Breakdown
        if (data.mode === 'jd_match') {
            const statMTarget = document.getElementById('stat-matched');
            if (statMTarget) statMTarget.textContent = data.primary_skills?.length || 0;
            
            const lblMatch = document.querySelector('#stat-matched + .stat-label');
            if(lblMatch) lblMatch.textContent = "Primary Matches";
            
            const lblMiss = document.querySelector('#stat-missing + .stat-label');
            if(lblMiss) lblMiss.textContent = "Missing Skills";

            renderJDBreakdown(data.breakdown, data);
            renderJDSkills(data);
        } else {
            renderBreakdown(data.breakdown);
            renderSkills(data.matched_skills, 'matched-skills-list', 'matched');
            renderSkills(data.missing_skills, 'missing-skills-list', 'missing');
            renderRankings(data.all_roles_analysis);
        }

        // 5. Recommendations
        renderRecommendations(data.recommendations);
        
        // 6. Certifications
        renderCertifications(data.certifications);

        // Buttons
        setupResultButtons();
    }

    function renderJDBreakdown(bd, data) {
        const container = document.getElementById('breakdown-container');
        if (!container || !bd) return;
        container.innerHTML = `
            <div class="breakdown-row">
                <div class="bd-header"><span class="bd-label">Skill Match Score (70% Weight)</span><span class="bd-value">${bd.skillMatch}%</span></div>
                <div class="progress-bar"><div class="progress-fill" style="width: ${bd.skillMatch}%; background: var(--neon-cyan)"></div></div>
                <div class="bd-sub" style="margin-bottom: 20px;">Direct overlap between resume and JD skills.</div>
            </div>
            <div class="breakdown-row">
                <div class="bd-header"><span class="bd-label">Keyword/Context Match (30% Weight)</span><span class="bd-value">${bd.contextMatch}%</span></div>
                <div class="progress-bar"><div class="progress-fill" style="width: ${bd.contextMatch}%; background: var(--neon-purple)"></div></div>
                <div class="bd-sub" style="margin-bottom: 20px;">Relevance of context (tools, architecture, responsibilities).</div>
            </div>
            ${data.why_explanation ? `<div style="padding: 18px; border-radius: 12px; background: rgba(0,245,255,0.05); border: 1px solid rgba(0,245,255,0.2); font-size:13px; color: var(--text-secondary); line-height: 1.6; margin-top: 20px;"><strong>💡 Analysis Details</strong><br/><span style="margin-top: 6px; display: inline-block;">${data.why_explanation}</span></div>` : ''}
        `;
    }

    function renderJDSkills(data) {
        const skillsSection = document.getElementById('skills-section');
        if(!skillsSection) return;
        const rightCard = skillsSection.children[1];
        if(!rightCard) return;

        rightCard.innerHTML = `
            <div class="section-title" style="color:var(--neon-green)">🟢 Primary Skills</div>
            <p style="font-size:12px; color:var(--text-muted); margin-bottom:8px;">Present in BOTH Resume & JD.</p>
            <div id="primary-skills-list" style="margin-bottom:24px; display:flex; flex-wrap:wrap; gap:8px;"></div>
            
            <div class="section-title" style="color:#ffab00">🟡 Secondary Skills</div>
            <p style="font-size:12px; color:var(--text-muted); margin-bottom:8px;">Partial matches or related skills.</p>
            <div id="secondary-skills-list" style="margin-bottom:24px; display:flex; flex-wrap:wrap; gap:8px;"></div>
            
            <div class="section-title" style="color:var(--neon-blue)">🔵 Bonus Skills</div>
            <p style="font-size:12px; color:var(--text-muted); margin-bottom:8px;">Extra value skills in your Resume.</p>
            <div id="bonus-skills-list" style="margin-bottom:24px; display:flex; flex-wrap:wrap; gap:8px;"></div>
            
            <div class="section-title" style="color:#ff6666;">❌ Missing Skills</div>
            <p style="font-size:12px; color:var(--text-muted); margin-bottom:8px;">Required by JD but missing.</p>
            <div id="jd-missing-skills-list" style="display:flex; flex-wrap:wrap; gap:8px;"></div>
        `;
        
        renderSkills(data.primary_skills, 'primary-skills-list', 'tier-primary');
        renderSkills(data.secondary_skills, 'secondary-skills-list', 'tier-secondary');
        renderSkills(data.bonus_skills, 'bonus-skills-list', 'tier-bonus');
        renderSkills(data.missing_skills, 'jd-missing-skills-list', 'missing');

        const jobsSection = document.getElementById('jobs-section');
        if (jobsSection) jobsSection.style.display = 'none';
        
        const links = document.querySelectorAll('.jump-link');
        links.forEach(l => {
            if(l.href.includes('#jobs-section')) l.style.display = 'none';
        });
    }

    function setupResultButtons() {
        ['new-analysis-btn', 'new-analysis-btn-bottom'].forEach(id => {
            const btn = document.getElementById(id);
            if (btn) btn.onclick = () => window.location.href = 'dashboard.html';
        });

        ['export-btn', 'export-btn-bottom'].forEach(id => {
            const btn = document.getElementById(id);
            if (btn) btn.onclick = () => exportReport();
        });
    }

    function renderBreakdown(breakdown) {
        const container = document.getElementById('breakdown-container');
        if (!container || !breakdown) return;
        container.innerHTML = '';

        Object.entries(breakdown).forEach(([tier, info]) => {
            const row = document.createElement('div');
            row.className = 'breakdown-row';
            row.innerHTML = `
                <div class="bd-header">
                    <span class="bd-label">${tier.toUpperCase()} Skills</span>
                    <span class="bd-value">${info.percentage}%</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${info.percentage}%; background: var(--neon-${getTierColor(tier)})"></div>
                </div>
                <div class="bd-sub">${info.matched.length} of ${info.total} matched (Weight: ${info.weight * 100}%)</div>
            `;
            container.appendChild(row);
        });
    }

    function getTierColor(tier) {
        if (tier === 'core') return 'cyan';
        if (tier === 'secondary') return 'purple';
        return 'green';
    }

    function renderSkills(skills, containerId, type) {
        const container = document.getElementById(containerId);
        if (!container) return;
        container.innerHTML = '';
        
        if (!skills || skills.length === 0) {
            container.innerHTML = `<p class="empty-note">No ${type} skills identified.</p>`;
            return;
        }

        skills.forEach(skill => {
            const chip = document.createElement('span');
            chip.className = `skill-chip ${type}`;
            chip.textContent = typeof skill === 'string' ? skill : skill.skill;
            container.appendChild(chip);
        });
    }

    function renderRecommendations(recs) {
        const container = document.getElementById('recommendations-list');
        if (!container) return;
        container.innerHTML = '';

        if (!recs || recs.length === 0) {
            container.innerHTML = '<p class="empty-note">No specific recommendations at this time.</p>';
            return;
        }

        recs.forEach(rec => {
            const card = document.createElement('div');
            card.className = 'rec-card';
            card.innerHTML = `
                <div class="rec-icon">💡</div>
                <div class="rec-body">
                    <div class="rec-title">${rec.key}</div>
                    <div class="rec-desc">${rec.text}</div>
                    <span class="rec-tag tag-${rec.priority}">${rec.priority.toUpperCase()} PRIORITY</span>
                </div>
            `;
            container.appendChild(card);
        });
    }

    function renderCertifications(certs) {
        const container = document.getElementById('certifications-list');
        if (!container) return;
        container.innerHTML = '';

        if (!certs || certs.length === 0) {
            container.innerHTML = '<p class="empty-note">No industry certifications listed for this category.</p>';
            return;
        }

        certs.forEach(cert => {
            const card = document.createElement('div');
            card.className = 'cert-card';
            card.innerHTML = `
                <div class="cert-icon">🎓</div>
                <div class="cert-body">
                    <div class="cert-name">${cert.name}</div>
                    <div class="cert-provider">${cert.provider}</div>
                </div>
                <div class="cert-badge">Official</div>
            `;
            container.appendChild(card);
        });
    }

    function renderRankings(analysis) {
        const container = document.getElementById('all-roles-list');
        if (!container || !analysis) return;
        container.innerHTML = '';

        const sorted = Object.entries(analysis).sort((a,b) => b[1].match_percentage - a[1].match_percentage);

        sorted.forEach(([cat, data], index) => {
            const row = document.createElement('div');
            row.className = `role-rank-row ${index === 0 ? 'top-role' : ''}`;
            row.innerHTML = `
                <div class="rank-meta">
                    <div class="rank-pos">${index + 1}</div>
                    <div class="rank-icon">${data.icon || '🚀'}</div>
                    <div class="rank-info">
                        <div class="rank-name">${cat}</div>
                        <div class="rank-roles">${(data.roles && data.roles.length > 0) ? data.roles.join(', ') : 'Professional Role'}</div>
                    </div>
                </div>
                <div class="rank-bar-wrap">
                    <div class="rank-bar-bg">
                        <div class="rank-bar-fill" style="width: ${data.match_percentage}%; background: ${data.match_color}"></div>
                    </div>
                    <div class="rank-pct">${data.match_percentage}%</div>
                    <div class="rank-level" style="color: ${data.match_color}">${data.match_level}</div>
                </div>
            `;
            container.appendChild(row);
        });
    }

    function exportReport() {
        window.print();
    }

    // ── AUTHENTICATION ────────────────────────────

    async function initAuth() {
        const token = storage.get('sga_token');
        if (token) {
            try {
                const res = await fetch(`${API_BASE_URL}/auth/me`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                if (res.ok) {
                    const user = await res.json();
                    updateUIForAuth(user);
                } else {
                    storage.remove('sga_token');
                    updateUIForGuest();
                }
            } catch (err) {
                console.error("Auth check failed:", err);
                updateUIForGuest();
            }
        } else {
            updateUIForGuest();
        }

        // Setup login form
        const loginForm = document.getElementById('login-form');
        if (loginForm) {
            loginForm.onsubmit = async (e) => {
                e.preventDefault();
                const email = document.getElementById('login-email').value;
                const password = document.getElementById('login-password').value;
                const btn = loginForm.querySelector('.btn-auth');
                
                try {
                    btn.textContent = 'Signing In...';
                    const res = await fetch(`${API_BASE_URL}/auth/login`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ email, password })
                    });
                    
                    const data = await res.json();
                    if (res.ok && data.access_token) {
                        storage.set('sga_token', data.access_token);
                        window.location.href = 'dashboard.html';
                    } else {
                        alert(data.detail || "Login failed. Please check credentials.");
                    }
                } catch (err) {
                    alert("Network error.");
                } finally {
                    btn.textContent = 'Sign In';
                }
            };
        }

        // Setup register form
        const regForm = document.getElementById('register-form');
        if (regForm) {
            regForm.onsubmit = async (e) => {
                e.preventDefault();
                const name = document.getElementById('reg-name').value;
                const email = document.getElementById('reg-email').value;
                const password = document.getElementById('reg-password').value;
                const btn = regForm.querySelector('.btn-auth');
                
                try {
                    btn.textContent = 'Creating Account...';
                    const res = await fetch(`${API_BASE_URL}/auth/register`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ name, email, password })
                    });
                    
                    const data = await res.json();
                    if (res.ok && data.access_token) {
                        storage.set('sga_token', data.access_token);
                        window.location.href = 'dashboard.html';
                    } else {
                        alert(data.detail || "Registration failed. Email likely already registered.");
                    }
                } catch (err) {
                    alert("Network error.");
                } finally {
                    btn.textContent = 'Get Started';
                }
            };
        }
    }

    function togglePasswordVisibility(inputId) {
        const input = document.getElementById(inputId);
        if(!input) return;
        if (input.type === 'password') {
            input.type = 'text';
        } else {
            input.type = 'password';
        }
    }

    async function logoutUser() {
        const token = storage.get('sga_token');
        storage.remove('sga_token');
        if (token) {
            try {
                await fetch(`${API_BASE_URL}/auth/logout`, { 
                    method: 'POST',
                    headers: { 'Authorization': `Bearer ${token}` }
                });
            } catch(e) {}
        }
        window.location.href = 'login.html';
    }

    function updateUIForAuth(user) {
        const uName = document.getElementById('user-name');
        const uEmail = document.getElementById('user-email');
        const uAva = document.getElementById('user-avatar');
        
        if (uName) uName.textContent = user.name;
        if (uEmail) uEmail.textContent = user.email;
        if (uAva) uAva.textContent = user.name.charAt(0).toUpperCase();

        const logoutBtns = document.querySelectorAll('.logout-btn');
        logoutBtns.forEach(btn => {
            btn.innerHTML = '🚪 Logout';
            btn.onclick = logoutUser;
        });
        
        const navLinks = document.querySelector('.nav-links');
        if (navLinks) {
            navLinks.innerHTML = `
                <a href="job-descriptions.html" class="nav-link">Job Description</a>
                <a href="dashboard.html" class="nav-link">Dashboard</a>
                <a href="#" onclick="SGA.logoutUser(); return false;" class="btn-nav">Logout</a>
            `;
        }
    }

    function updateUIForGuest() {
        const uName = document.getElementById('user-name');
        const uEmail = document.getElementById('user-email');
        const uAva = document.getElementById('user-avatar');
        
        if (uName) uName.textContent = "Guest";
        if (uEmail) uEmail.textContent = "Not logged in";
        if (uAva) uAva.textContent = "G";

        const logoutBtns = document.querySelectorAll('.logout-btn');
        logoutBtns.forEach(btn => {
            btn.innerHTML = '🔑 Login';
            btn.onclick = () => window.location.href = 'login.html';
        });
    }

    // ── PUBLIC ────────────────────────────────────
    return {
        init,
        initResultPage,
        exportReport,
        togglePasswordVisibility,
        logoutUser
    };

})();

// Global init on load
document.addEventListener('DOMContentLoaded', () => {
    SGA.init();
    // Re-check if we are on results page
    if (document.getElementById('score-value')) {
        SGA.initResultPage();
    }
});

// Helper for resetting uploads (called from HTML)
function resetUpload() {
    location.reload();
}
function resetJDUpload() {
    location.reload();
}
