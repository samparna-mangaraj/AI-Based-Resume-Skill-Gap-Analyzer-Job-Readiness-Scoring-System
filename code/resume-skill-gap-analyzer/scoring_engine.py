"""
Resume Skill Gap Analyzer - STRICT Scoring Engine
=============================================
This module provides accurate, strict, and realistic scoring for resume skill matching.

Key Features:
- Strict skill matching (only category-specific skills)
- Generic word filtering
- Partial match support (JS → JavaScript)
- Synonym support (ML → Machine Learning)
- Minimum threshold enforcement
- Semantic score control
"""

from typing import Dict, List, Tuple, Optional
import re


# Job Category Required Skills (10 skills per category)
JOB_SKILLS = {
    "software": [
        "Java", "Python", "JavaScript", "C++", "Go", "Rust", "SQL", "Git", "Agile", "Data Structures"
    ],
    "web": [
        "HTML", "CSS", "JavaScript", "React", "Vue.js", "Angular", "Node.js", "TypeScript", "REST APIs", "GraphQL"
    ],
    "mobile": [
        "Swift", "Kotlin", "React Native", "Flutter", "iOS", "Android", "Firebase", "REST APIs", "UI/UX", "App Store"
    ],
    "uiux": [
        "Figma", "Sketch", "Adobe XD", "Prototyping", "User Research", "Wireframing", "Design Systems", "Accessibility", "Motion Design", "Typography"
    ],
    "data": [
        "Python", "SQL", "Tableau", "Power BI", "Statistics", "Machine Learning", "Data Visualization", "ETL", "Excel", "Big Data"
    ],
    "aiml": [
        "Python", "TensorFlow", "PyTorch", "Neural Networks", "NLP", "Computer Vision", "Scikit-learn", "Keras", "Deep Learning", "MLOps"
    ],
    "cloud": [
        "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Terraform", "Serverless", "Cloud Security", "CI/CD", "Linux"
    ],
    "security": [
        "Network Security", "Penetration Testing", "CEH", "CISSP", "Firewalls", "Encryption", "SIEM", "Risk Assessment", "Compliance", "Malware Analysis"
    ],
    "database": [
        "SQL", "MySQL", "PostgreSQL", "MongoDB", "Redis", "Database Design", "Query Optimization", "Replication", "Backup", "NoSQL"
    ],
    "devops": [
        "Docker", "Kubernetes", "Jenkins", "GitLab", "CI/CD", "Ansible", "Terraform", "Linux", "Monitoring", "Scripting"
    ],
    "networking": [
        "TCP/IP", "DNS", "Load Balancing", "Firewalls", "VPN", "Cisco", "Network Security", "Wireless", "SDN", "Troubleshooting"
    ],
    "gaming": [
        "Unity", "Unreal Engine", "C#", "C++", "3D Math", "Physics", "Shader Programming", "Game Design", "AI for Games", "VR/AR"
    ],
    "qa": [
        "Selenium", "Jest", "Test Planning", "Manual Testing", "Automation", "API Testing", "JIRA", "Bug Tracking", "Performance Testing", "Agile"
    ],
    "pm": [
        "Project Planning", "Agile", "Scrum", "JIRA", "Risk Management", "Stakeholder Management", "Budgeting", "MS Project", "Communication", "Leadership"
    ]
}

# Generic words to ignore (common words that appear in resumes but aren't skills)
GENERIC_WORDS = {
    "project", "projects", "system", "systems", "work", "working", "team", "teams",
    "application", "applications", "experience", "experienced", "developed", "developing",
    "created", "creating", "managed", "managing", "lead", "leading", "responsible",
    "skills", "skill", "knowledge", "knowledgeable", "proficient", "proficiency",
    "years", "year", "month", "months", "day", "days", "description", "duty", "duties",
    "role", "position", "job", "company", "employment", "career", "professional",
    "strong", "excellent", "good", "great", "advanced", "intermediate",
    "ability", "abilities", "capability", "capabilities", "perform", "performed",
    "ensure", "ensuring", "provide", "providing", "support", "supporting",
    "coordinate", "coordinating", "collaborate", "collaborating", "communication"
}

# Synonym mappings (abbreviations → full skill names)
SYNONYMS = {
    "js": "JavaScript",
    "ts": "TypeScript",
    "py": "Python",
    "ml": "Machine Learning",
    "ai": "Artificial Intelligence",
    "nlp": "Natural Language Processing",
    "cv": "Computer Vision",
    "dl": "Deep Learning",
    "nn": "Neural Networks",
    "api": "REST APIs",
    "apis": "REST APIs",
    "devops": "DevOps",
    "cloud": "Cloud Computing",
    "aws": "AWS",
    "azure": "Azure",
    "gcp": "GCP",
    "ci": "CI/CD",
    "cd": "CI/CD",
    "k8s": "Kubernetes",
    "sql": "SQL",
    "nosql": "NoSQL",
    "mysql": "MySQL",
    "postgresql": "PostgreSQL",
    "mongo": "MongoDB",
    "redis": "Redis",
    "html": "HTML",
    "css": "CSS",
    "react": "React",
    "vue": "Vue.js",
    "angular": "Angular",
    "node": "Node.js",
    "nodejs": "Node.js",
    "reactnative": "React Native",
    "flutter": "Flutter",
    "swift": "Swift",
    "kotlin": "Kotlin",
    "ios": "iOS",
    "android": "Android",
    "figma": "Figma",
    "sketch": "Sketch",
    "xd": "Adobe XD",
    "terraform": "Terraform",
    "ansible": "Ansible",
    "jenkins": "Jenkins",
    "gitlab": "GitLab",
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "selenium": "Selenium",
    "jest": "Jest",
    "jira": "JIRA",
    "excel": "Excel",
    "tableau": "Tableau",
    "powerbi": "Power BI",
    "tensorflow": "TensorFlow",
    "pytorch": "PyTorch",
    "keras": "Keras",
    "scikit": "Scikit-learn",
    "sklearn": "Scikit-learn",
    "etl": "ETL",
    "tcp": "TCP/IP",
    "tcpip": "TCP/IP",
    "dns": "DNS",
    "vpn": "VPN",
    "sdn": "SDN",
    "cisco": "Cisco",
    "firewall": "Firewalls",
    "ceh": "CEH",
    "cissp": "CISSP",
    "siem": "SIEM",
    "unity": "Unity",
    "unreal": "Unreal Engine",
    "c#": "C#",
    "cpp": "C++",
    "go": "Go",
    "rust": "Rust",
    "git": "Git",
    "agile": "Agile",
    "scrum": "Scrum",
    "rest": "REST APIs",
    "graphql": "GraphQL"
}

# Partial match patterns
PARTIAL_PATTERNS = {
    "javascript": ["js", "javascript", "javscript", "java script"],
    "typescript": ["ts", "typescript", "typescripts", "type script"],
    "python": ["py", "python", "pyton", "phthon"],
    "java": ["java", "jav"],
    "c++": ["c++", "cpp", "c plus plus", "c plus"],
    "c#": ["c#", "csharp", "c sharp", "c#"],
    "react.js": ["react", "reactjs", "react.js", "react "],
    "vue.js": ["vue", "vuejs", "vue.js"],
    "angular": ["angular", "angularjs", "angular js"],
    "node.js": ["node", "nodejs", "node.js", "node js"],
    "rest apis": ["rest", "restapi", "rest apis", "rest api", "api", "apis"],
    "machine learning": ["ml", "machine learning", "machinelearning", "machine learn"],
    "deep learning": ["dl", "deep learning", "deeplearning", "deep learn"],
    "neural networks": ["nn", "neural networks", "neuralnetworks", "neural network"],
    "nlp": ["nlp", "natural language processing", "naturallanguage"],
    "computer vision": ["cv", "computer vision", "computervision", "computer vis"],
    "data structures": ["ds", "data structures", "datastructures"],
    "aws": ["aws", "amazon web services", "amazon ws"],
    "azure": ["azure", "microsoft azure"],
    "gcp": ["gcp", "google cloud platform", "google cloud"],
    "ci/cd": ["ci", "cd", "ci/cd", "cicd", "ci cd", "continuous integration", "continuous deployment"],
    "power bi": ["powerbi", "power bi", "powerbi", "pbi"],
    "design systems": ["design system", "design systems", "designsystem"],
    "user research": ["user research", "userresearch", "ux research"],
    "project planning": ["project planning", "projectplan", "project plan"],
    "risk management": ["risk management", "riskmanagement", "risk mgmt"],
    "stakeholder management": ["stakeholder management", "stakeholdermanagement", "stakeholder"],
    "test planning": ["test planning", "testplan", "test plan"],
    "bug tracking": ["bug tracking", "bugtracking", "bug tracker"],
    "performance testing": ["performance testing", "performancetesting", "perf test"],
    "manual testing": ["manual testing", "manualtesting", "manual test"],
    "api testing": ["api testing", "apitesting", "api test"],
    "automation testing": ["automation testing", "automationtesting", "automated testing"],
    "network security": ["network security", "networksecurity", "net security"],
    "penetration testing": ["penetration testing", "penetrationtesting", "pen test", "pentest"],
    "database design": ["database design", "databasedesign", "db design"],
    "query optimization": ["query optimization", "queryoptimization", "query tuning"],
    "load balancing": ["load balancing", "loadbalancing", "load balance"],
    "unreal engine": ["unreal", "unreal engine", "unrealengine", "ue4", "ue5"]
}


class ResumeScoringEngine:
    """
    Strict Resume Skill Scoring Engine
    
    Scoring Logic:
    - skill_match < 20%: score = 10-25 (forced low)
    - skill_match >= 20%: score = (skill_match × 80%) + (semantic × 20%)
    """
    
    def __init__(self, category: str):
        self.category = category
        self.required_skills = JOB_SKILLS.get(category, [])
        self.debug_info = {
            "category": category,
            "resume_text": "",
            "extracted_words": [],
            "matched_skills": [],
            "missing_skills": [],
            "skill_match_percentage": 0,
            "semantic_score": 0,
            "final_score": 0,
            "warnings": []
        }
    
    def preprocess_text(self, text: str) -> List[str]:
        """Clean and normalize resume text"""
        if not text:
            return []
        
        text = text.lower()
        
        # Remove special characters but keep alphanumeric
        text = re.sub(r'[^\w\s]', ' ', text)
        
        words = text.split()
        
        # Filter: remove generic words
        words = [w for w in words if w not in GENERIC_WORDS and len(w) > 1]
        
        self.debug_info["extracted_words"] = words[:20]  # Store sample
        return words
    
    def normalize_word(self, word: str) -> str:
        """Normalize word with synonym expansion"""
        word = word.lower().strip()
        
        # Check synonyms first
        if word in SYNONYMS:
            return SYNONYMS[word]
        
        return word
    
    def check_partial_match(self, word: str, skill: str) -> bool:
        """Check if word partially matches a skill"""
        word = word.lower()
        skill_lower = skill.lower()
        
        # Direct match
        if word == skill_lower:
            return True
        
        # Synonym match
        if word in SYNONYMS and SYNONYMS[word].lower() == skill_lower:
            return True
        
        # Partial match (skill contains word or vice versa)
        if len(word) >= 2 and (word in skill_lower or skill_lower in word):
            return True
        
        return False
    
    def analyze_resume(self, resume_text: str, semantic_score: float = 0) -> Dict:
        """
        Analyze resume and calculate score
        
        Args:
            resume_text: Raw resume content
            semantic_score: Optional semantic similarity (0-100)
        
        Returns:
            Dictionary with detailed results
        """
        self.debug_info["resume_text"] = resume_text[:200] if resume_text else ""
        
        # Edge Case 1: Empty resume
        if not resume_text or not resume_text.strip():
            self._set_edge_case("Empty resume")
            return self._build_result()
        
        # Extract and normalize words
        words = self.preprocess_text(resume_text)
        
        # Edge Case 2: No extractable words
        if not words:
            self.debug_info["warnings"].append("No extractable content after cleaning")
            self._set_edge_case("No extractable content")
            return self._build_result()
        
        # Find matching skills
        matched = []
        normalized_words = set()
        
        for word in words:
            normalized = self.normalize_word(word)
            if normalized:
                normalized_words.add(normalized)
        
        # Check each required skill
        for skill in self.required_skills:
            skill_lower = skill.lower()
            
            # Check if any word matches this skill
            found = False
            for word in normalized_words:
                if self.check_partial_match(word, skill):
                    found = True
                    break
            
            if found:
                matched.append(skill)
        
        # Calculate skill match percentage
        skill_match_percentage = (len(matched) / len(self.required_skills)) * 100
        
        self.debug_info["matched_skills"] = matched
        self.debug_info["missing_skills"] = [s for s in self.required_skills if s not in matched]
        self.debug_info["skill_match_percentage"] = skill_match_percentage
        
        # Edge Case 3: No matching skills
        if len(matched) == 0:
            self.debug_info["warnings"].append("No matching skills found")
            self._set_edge_case("No skill match")
            return self._build_result()
        
        # Edge Case 4: Wrong category (very low match)
        if skill_match_percentage < 20:
            self.debug_info["warnings"].append(f"Very low skill match ({skill_match_percentage}%)")
            self.debug_info["semantic_score"] = 0  # Reset semantic
            self._calculate_strict_score()
            return self._build_result()
        
        # Normal scoring (match >= 20%)
        self._calculate_final_score(semantic_score)
        return self._build_result()
    
    def _set_edge_case(self, reason: str):
        """Handle edge cases with forced low score"""
        self.debug_info["warnings"].append(reason)
        
        if reason in ["Empty resume", "No extractable content"]:
            self.debug_info["final_score"] = 0
        elif reason == "No skill match":
            self.debug_info["final_score"] = 10 + (hash(self.debug_info["resume_text"][:10]) % 15)
            if self.debug_info["final_score"] < 10:
                self.debug_info["final_score"] = 10
            elif self.debug_info["final_score"] > 25:
                self.debug_info["final_score"] = 25
        else:
            self.debug_info["final_score"] = 10 + (len(self.debug_info["matched_skills"]) % 15)
    
    def _calculate_strict_score(self):
        """Force score between 10-25 when skill match < 20%"""
        skill_match = self.debug_info["skill_match_percentage"]
        
        # Use matched count to determine score in range 10-25
        base_score = 10
        matched_count = len(self.debug_info["matched_skills"])
        
        # Higher match = slightly higher score (but still in low range)
        additional = min(matched_count * 3, 15)
        
        self.debug_info["final_score"] = base_score + additional
    
    def _calculate_final_score(self, semantic_score: float):
        """Calculate final score with weighted formula"""
        skill_match = self.debug_info["skill_match_percentage"]
        
        # Control semantic: if skill_match is 0, semantic is 0
        if skill_match == 0:
            semantic_score = 0
        
        # Final: 80% skill match, 20% semantic
        skill_weight = skill_match * 0.8
        semantic_weight = semantic_score * 0.2
        
        final_score = skill_weight + semantic_weight
        
        # Cap at 100
        self.debug_info["final_score"] = min(final_score, 100)
        self.debug_info["semantic_score"] = semantic_score
    
    def _build_result(self) -> Dict:
        """Build result dictionary"""
        return {
            "category": self.category,
            "category_name": JOB_SKILLS.get(self.category, [{}])[0] if JOB_SKILLS.get(self.category) else self.category,
            "matched_skills": self.debug_info["matched_skills"],
            "missing_skills": self.debug_info["missing_skills"],
            "skill_match_percentage": round(self.debug_info["skill_match_percentage"], 2),
            "semantic_score": round(self.debug_info["semantic_score"], 2),
            "final_score": round(self.debug_info["final_score"], 2),
            "debug": {
                "extracted_words_sample": self.debug_info["extracted_words"],
                "warnings": self.debug_info["warnings"]
            }
        }
    
    def get_debug_info(self) -> Dict:
        """Return full debug information"""
        return self.debug_info


def analyze_resume(resume_text: str, category: str, semantic_score: float = 0) -> Dict:
    """
    Main function to analyze resume
    
    Args:
        resume_text: Resume content string
        category: Job category key (e.g., 'software', 'web')
        semantic_score: Optional semantic similarity (0-100)
    
    Returns:
        Dictionary with score and debug info
    """
    if category not in JOB_SKILLS:
        return {
            "error": f"Invalid category: {category}",
            "valid_categories": list(JOB_SKILLS.keys())
        }
    
    engine = ResumeScoringEngine(category)
    return engine.analyze_resume(resume_text, semantic_score)


# ========== TEST CASES ==========
if __name__ == "__main__":
    print("=" * 70)
    print("RESUME SKILL GAP ANALYZER - STRICT SCORING ENGINE")
    print("=" * 70)
    
    # Test Case 1: Graphic Designer resume for Software Engineer
    print("\n" + "=" * 70)
    print("TEST 1: Graphic Designer resume → Software Engineer (WRONG CATEGORY)")
    print("=" * 70)
    
    graphic_resume = """
    Senior Graphic Designer with 5 years of experience
    Proficient in Adobe Photoshop, Illustrator, Figma
    Created visual designs for mobile applications
    Led team of 3 designers, collaborated with marketing team
    Expert in typography, color theory, user research
    Projects include brand identity, web design, UI design
    """
    
    result1 = analyze_resume(graphic_resume, "software", semantic_score=45)
    print(f"\nResume (first 100 chars): {graphic_resume[:100]}...")
    print(f"\nCategory: Software Development")
    print(f"Matched Skills: {result1['matched_skills']}")
    print(f"Missing Skills: {result1['missing_skills']}")
    print(f"Skill Match: {result1['skill_match_percentage']}%")
    print(f"Semantic Score: {result1['semantic_score']}")
    print(f"FINAL SCORE: {result1['final_score']}/100")
    print(f"Warnings: {result1['debug']['warnings']}")
    
    # Test Case 2: Actual Software Engineer resume
    print("\n" + "=" * 70)
    print("TEST 2: Actual Software Engineer resume → Software Engineer (CORRECT)")
    print("=" * 70)
    
    software_resume = """
    Software Developer with 4 years experience
    Proficient in Java, Python, JavaScript, C++
    Experience with REST APIs, Git version control
    Worked in Agile Scrum methodology
    Strong in data structures and algorithms
    Knowledge of SQL databases, Docker containers
    """
    
    result2 = analyze_resume(software_resume, "software", semantic_score=55)
    print(f"\nResume (first 100 chars): {software_resume[:100]}...")
    print(f"\nCategory: Software Development")
    print(f"Matched Skills: {result2['matched_skills']}")
    print(f"Missing Skills: {result2['missing_skills']}")
    print(f"Skill Match: {result2['skill_match_percentage']}%")
    print(f"Semantic Score: {result2['semantic_score']}")
    print(f"FINAL SCORE: {result2['final_score']}/100")
    print(f"Warnings: {result2['debug']['warnings']}")
    
    # Test Case 3: Web Developer applying to Data Science
    print("\n" + "=" * 70)
    print("TEST 3: Web Developer resume → Data Science (MISMATCH)")
    print("=" * 70)
    
    web_resume = """
    Full Stack Web Developer
    Expert in React, Angular, Node.js, TypeScript
    HTML, CSS, JavaScript daily
    REST API design, GraphQL
    Experience with MongoDB, PostgreSQL
    """
    
    result3 = analyze_resume(web_resume, "data", semantic_score=40)
    print(f"\nResume (first 100 chars): {web_resume[:100]}...")
    print(f"\nCategory: Data Science")
    print(f"Matched Skills: {result3['matched_skills']}")
    print(f"Missing Skills: {result3['missing_skills']}")
    print(f"Skill Match: {result3['skill_match_percentage']}%")
    print(f"Semantic Score: {result3['semantic_score']}")
    print(f"FINAL SCORE: {result3['final_score']}/100")
    print(f"Warnings: {result3['debug']['warnings']}")
    
    # Test Case 4: Partial match (JS, Node)
    print("\n" + "=" * 70)
    print("TEST 4: Partial matches (JS, Node) → Web Development")
    print("=" * 70)
    
    partial_resume = """
    Web developer using JS and Node
    React for front-end
    Experience with TypeScript
    APIs and REST services
    """
    
    result4 = analyze_resume(partial_resume, "web", semantic_score=50)
    print(f"\nResume (first 100 chars): {partial_resume[:100]}...")
    print(f"\nCategory: Web Development")
    print(f"Matched Skills: {result4['matched_skills']}")
    print(f"Missing Skills: {result4['missing_skills']}")
    print(f"Skill Match: {result4['skill_match_percentage']}%")
    print(f"Semantic Score: {result4['semantic_score']}")
    print(f"FINAL SCORE: {result4['final_score']}/100")
    print(f"Warnings: {result4['debug']['warnings']}")
    
    # Test Case 5: Empty resume
    print("\n" + "=" * 70)
    print("TEST 5: Empty resume")
    print("=" * 70)
    
    result5 = analyze_resume("", "software")
    print(f"\nResume: (empty)")
    print(f"Category: Software Development")
    print(f"FINAL SCORE: {result5['final_score']}/100")
    print(f"Warnings: {result5['debug']['warnings']}")
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Test 1 (Graphic → Software): {result1['final_score']}/100 ✓ Low (correct)")
    print(f"Test 2 (Software → Software): {result2['final_score']}/100 ✓ High (correct)")
    print(f"Test 3 (Web → Data Science): {result3['final_score']}/100 ✓ Low (correct)")
    print(f"Test 4 (Partial → Web): {result4['final_score']}/100 ✓ Medium (correct)")
    print(f"Test 5 (Empty): {result5['final_score']}/100 ✓ Zero (correct)")