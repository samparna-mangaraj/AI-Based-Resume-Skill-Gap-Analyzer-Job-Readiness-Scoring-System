"""
Resume Skill Matching System - STRICT PERCENTAGE CALCULATOR
==================================================
Mathematical skill matching using exact set intersection.
"""

from typing import Dict, List, Set


# ============================================
# JOB CATEGORIES & FULL SKILL SETS
# ============================================

JOB_SKILLS = {
    "software": [
        "JavaScript", "Python", "Java", "C++", "React", "Node.js", "Django", "APIs", "DSA", "SQL", "MongoDB", "Git"
    ],
    "web": [
        "HTML", "CSS", "JavaScript", "Bootstrap", "Tailwind", "SEO", "Responsive Design"
    ],
    "mobile": [
        "Kotlin", "Java", "Swift", "Flutter", "React Native", "Firebase", "APIs"
    ],
    "uiux": [
        "Figma", "Adobe XD", "Wireframing", "Prototyping", "User Research"
    ],
    "data": [
        "Python", "R", "SQL", "Excel", "Power BI", "Tableau", "Statistics"
    ],
    "aiml": [
        "Python", "TensorFlow", "PyTorch", "NLP", "Deep Learning"
    ],
    "cloud": [
        "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Linux"
    ],
    "security": [
        "Networking", "Kali Linux", "Metasploit", "Cryptography"
    ],
    "database": [
        "SQL", "Database Design", "Hadoop", "Spark", "ETL"
    ],
    "devops": [
        "Docker", "Kubernetes", "CI/CD", "Bash", "Python", "Terraform"
    ],
    "networking": [
        "Networking", "LAN", "WAN", "Linux", "Windows", "Troubleshooting"
    ],
    "gaming": [
        "Unity", "Unreal", "C#", "C++", "Game Physics", "Animation"
    ],
    "qa": [
        "Manual Testing", "Selenium", "Cypress", "Test Cases", "JIRA"
    ],
    "pm": [
        "Agile", "Scrum", "Jira", "Trello", "Communication"
    ]
}

CATEGORY_NAMES = {
    "software": "Software Development",
    "web": "Web Development",
    "mobile": "Mobile Development",
    "uiux": "UI/UX Design",
    "data": "Data Science & Analytics",
    "aiml": "AI / Machine Learning",
    "cloud": "Cloud Computing",
    "security": "Cybersecurity",
    "database": "Database Engineering",
    "devops": "DevOps",
    "networking": "Networking / IT Support",
    "gaming": "Game Development",
    "qa": "QA / Testing",
    "pm": "Project Management"
}


# ============================================
# SYNONYMS & PARTIAL MATCHES
# ============================================

SKILL_NORMALIZATIONS = {
    # JavaScript
    "js": "JavaScript",
    "javascript": "JavaScript",
    
    # Python
    "py": "Python",
    "python": "Python",
    
    # Java
    "java": "Java",
    
    # C++
    "c++": "C++",
    "cpp": "C++",
    "c plus plus": "C++",
    
    # C#
    "c#": "C#",
    "csharp": "C#",
    
    # React
    "react": "React",
    "reactjs": "React",
    "react.js": "React",
    
    # React Native
    "reactnative": "React Native",
    "react-native": "React Native",
    "react native": "React Native",
    
    # Node.js
    "node": "Node.js",
    "nodejs": "Node.js",
    "node.js": "Node.js",
    
    # Django
    "django": "Django",
    
    # APIs
    "api": "APIs",
    "apis": "APIs",
    "rest": "APIs",
    "rest api": "APIs",
    
    # DSA
    "dsa": "DSA",
    "data structures": "DSA",
    "algorithms": "DSA",
    
    # SQL
    "sql": "SQL",
    "mysql": "SQL",
    "postgresql": "SQL",
    
    # MongoDB
    "mongodb": "MongoDB",
    "mongo": "MongoDB",
    
    # Git
    "git": "Git",
    "github": "Git",
    
    # OOP
    "oop": "OOP",
    "object oriented": "OOP",
    
    # HTML
    "html": "HTML",
    "html5": "HTML",
    
    # CSS
    "css": "CSS",
    "css3": "CSS",
    
    # Bootstrap
    "bootstrap": "Bootstrap",
    
    # Tailwind
    "tailwind": "Tailwind",
    "tailwindcss": "Tailwind",
    
    # SEO
    "seo": "SEO",
    "search engine": "SEO",
    
    # Responsive Design
    "responsive": "Responsive Design",
    "responsive design": "Responsive Design",
    "mobile responsive": "Responsive Design",
    
    # Kotlin
    "kotlin": "Kotlin",
    
    # Swift
    "swift": "Swift",
    
    # Flutter
    "flutter": "Flutter",
    
    # Firebase
    "firebase": "Firebase",
    
    # Figma
    "figma": "Figma",
    
    # Adobe XD
    "adobe xd": "Adobe XD",
    "xd": "Adobe XD",
    
    # Wireframing
    "wireframe": "Wireframing",
    "wireframing": "Wireframing",
    
    # Prototyping
    "prototype": "Prototyping",
    "prototyping": "Prototyping",
    
    # User Research
    "user research": "User Research",
    "ux research": "User Research",
    
    # R
    "r": "R",
    "r programming": "R",
    "r language": "R",
    
    # Excel
    "excel": "Excel",
    "microsoft excel": "Excel",
    
    # Power BI
    "power bi": "Power BI",
    "powerbi": "Power BI",
    
    # Tableau
    "tableau": "Tableau",
    
    # Statistics
    "statistics": "Statistics",
    "stats": "Statistics",
    
    # TensorFlow
    "tensorflow": "TensorFlow",
    "tf": "TensorFlow",
    
    # PyTorch
    "pytorch": "PyTorch",
    "torch": "PyTorch",
    
    # NLP
    "nlp": "NLP",
    "natural language": "NLP",
    
    # Deep Learning
    "deep learning": "Deep Learning",
    "dl": "Deep Learning",
    
    # AWS
    "aws": "AWS",
    "amazon web": "AWS",
    
    # Azure
    "azure": "Azure",
    "microsoft azure": "Azure",
    
    # GCP
    "gcp": "GCP",
    "google cloud": "GCP",
    
    # Docker
    "docker": "Docker",
    "containers": "Docker",
    
    # Kubernetes
    "kubernetes": "Kubernetes",
    "k8s": "Kubernetes",
    
    # Linux
    "linux": "Linux",
    "unix": "Linux",
    
    # Networking
    "networking": "Networking",
    "network security": "Networking",
    
    # Kali Linux
    "kali": "Kali Linux",
    "kali linux": "Kali Linux",
    
    # Metasploit
    "metasploit": "Metasploit",
    "metasploitable": "Metasploit",
    
    # Cryptography
    "crypto": "Cryptography",
    "cryptography": "Cryptography",
    "encryption": "Cryptography",
    
    # Database Design
    "database design": "Database Design",
    "db design": "Database Design",
    "schema": "Database Design",
    
    # Hadoop
    "hadoop": "Hadoop",
    "hdfs": "Hadoop",
    
    # Spark
    "spark": "Spark",
    "pyspark": "Spark",
    
    # ETL
    "etl": "ETL",
    "data pipeline": "ETL",
    
    # CI/CD
    "ci cd": "CI/CD",
    "ci/cd": "CI/CD",
    "cicd": "CI/CD",
    "jenkins": "CI/CD",
    
    # Bash
    "bash": "Bash",
    "shell": "Bash",
    "sh": "Bash",
    
    # Terraform
    "terraform": "Terraform",
    "tf": "Terraform",
    
    # LAN
    "lan": "LAN",
    "local area network": "LAN",
    
    # WAN
    "wan": "WAN",
    "wide area network": "WAN",
    
    # Windows
    "windows": "Windows",
    "windows server": "Windows",
    
    # Troubleshooting
    "troubleshoot": "Troubleshooting",
    "troubleshooting": "Troubleshooting",
    
    # Unity
    "unity": "Unity",
    "unity3d": "Unity",
    "unity 3d": "Unity",
    
    # Unreal
    "unreal": "Unreal",
    "unreal engine": "Unreal",
    "ue4": "Unreal",
    "ue5": "Unreal",
    
    # Game Physics
    "physics": "Game Physics",
    "game physics": "Game Physics",
    
    # Animation
    "animation": "Animation",
    "2d animation": "Animation",
    "3d animation": "Animation",
    
    # Manual Testing
    "manual testing": "Manual Testing",
    "manual test": "Manual Testing",
    
    # Selenium
    "selenium": "Selenium",
    "selenium webdriver": "Selenium",
    
    # Cypress
    "cypress": "Cypress",
    "e2e testing": "Cypress",
    
    # Test Cases
    "test case": "Test Cases",
    "test cases": "Test Cases",
    "tc": "Test Cases",
    
    # JIRA
    "jira": "JIRA",
    "jira issues": "JIRA",
    
    # Agile
    "agile": "Agile",
    "agile methodology": "Agile",
    
    # Scrum
    "scrum": "Scrum",
    "scrum methodology": "Scrum",
    
    # Trello
    "trello": "Trello",
    "kanban": "Trello",
    
    # Communication
    "communication": "Communication",
    "communication skills": "Communication",
}


# ============================================
# GENERIC WORDS TO REMOVE
# ============================================

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
    "coordinate", "coordinating", "collaborate", "collaborating", "communication",
    "design", "designed", "designing", "build", "built", "building",
    "implement", "implemented", "implementing"
}


def normalize_text(text: str) -> str:
    """Convert text to lowercase and normalize"""
    if not text:
        return ""
    return text.lower().strip()


def extract_skills_from_text(text: str) -> Set[str]:
    """Extract skills from resume text using normalization"""
    if not text:
        return set()
    
    # Normalize text
    text = normalize_text(text)
    
    # Remove punctuation but keep ++ and # for C++ and C#
    import re
    text = text.replace("++", " PLUSPLUS ")
    text = text.replace("#", "HASH")
    text = re.sub(r'[^\w\s]', ' ', text)
    text = text.replace("PLUSPLUS", "c++")
    text = text.replace("HASH", "C")
    text = re.sub(r'\s+', ' ', text)
    
    words = text.split()
    
    # Remove generic words
    words = [w for w in words if w not in GENERIC_WORDS and len(w) > 1]
    
    # Normalize each word using synonym map and build skill set
    extracted_skills = set()
    
    for word in words:
        # Check direct normalization
        if word in SKILL_NORMALIZATIONS:
            extracted_skills.add(SKILL_NORMALIZATIONS[word])
            continue
        
        # Check partial match
        for key, value in SKILL_NORMALIZATIONS.items():
            if key in word or word in key:
                extracted_skills.add(value)
                break
        else:
            # Check if word itself is a skill (after title case check)
            title_word = word.title()
            for skill in get_all_skills():
                if normalize_text(skill) == word:
                    extracted_skills.add(skill)
                elif word in normalize_text(skill):
                    extracted_skills.add(skill)
    
    return extracted_skills


def get_all_skills() -> List[str]:
    """Get all skills across all categories"""
    all_skills = set()
    for skills in JOB_SKILLS.values():
        all_skills.update(skills)
    return list(all_skills)


def calculate_match_percentage(
    resume_text: str,
    category: str
) -> Dict:
    """
    Calculate EXACT match percentage using set intersection.
    
    Formula: score = (matched_count / total_count) × 100
    """
    
    # Validate category
    if category not in JOB_SKILLS:
        return {
            "error": f"Invalid category: {category}",
            "valid_categories": list(JOB_SKILLS.keys())
        }
    
    # Edge case: Empty resume
    if not resume_text or not resume_text.strip():
        return {
            "selected_category": category,
            "category_name": CATEGORY_NAMES.get(category, category),
            "total_required_skills": len(JOB_SKILLS[category]),
            "matched_skills": [],
            "missing_skills": JOB_SKILLS[category],
            "match_percentage": 0
        }
    
    # Get job skills for the category
    job_skills_set = set(JOB_SKILLS[category])
    
    # Extract skills from resume
    resume_skills_set = extract_skills_from_text(resume_text)
    
    # Calculate exact match using set intersection
    matched_skills = job_skills_set & resume_skills_set
    missing_skills = job_skills_set - resume_skills_set
    
    # Calculate percentage: (matched / total) × 100
    matched_count = len(matched_skills)
    total_count = len(job_skills_set)
    match_percentage = (matched_count / total_count) * 100 if total_count > 0 else 0
    
    return {
        "selected_category": category,
        "category_name": CATEGORY_NAMES.get(category, category),
        "total_required_skills": total_count,
        "matched_skills": sorted(list(matched_skills)),
        "missing_skills": sorted(list(missing_skills)),
        "match_percentage": round(match_percentage, 2)
    }


# ============================================
# TEST CASES
# ============================================

if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    
    print("=" * 70)
    print("STRICT PERCENTAGE CALCULATOR - TEST CASES")
    print("=" * 70)
    
    # Test Case 1: Only 6 skills
    print("\n" + "-" * 70)
    print("TEST 1: ONLY 6 skills -> SHOULD BE 50%")
    print("-" * 70)
    
    resume1 = "JavaScript Python Java React Node.js Django"
    result1 = calculate_match_percentage(resume1, "software")
    print("Resume skills:", resume1)
    print("Category: Software Development")
    print("Total Skills:", result1["total_required_skills"])
    print("Matched:", result1["matched_skills"])
    print("MATCH PERCENTAGE:", result1["match_percentage"], "%")
    print("Expected: 50% (6/12)")
    
    # Test Case 2: Wrong category -> 0%
    print("\n" + "-" * 70)
    print("TEST 2: Wrong category -> SHOULD BE 0%")
    print("-" * 70)
    
    resume2 = "Adobe Photoshop Illustrator Figma wireframing"
    result2 = calculate_match_percentage(resume2, "software")
    print("Resume: Design skills (wrong category)")
    print("Category: Software Development")
    print("Total Skills:", result2["total_required_skills"])
    print("Matched:", result2["matched_skills"])
    print("MATCH PERCENTAGE:", result2["match_percentage"], "%")
    print("Expected: 0% (no software skills)")
    
    # Test Case 3: Full match -> 100%
    print("\n" + "-" * 70)
    print("TEST 3: All 12 skills -> SHOULD BE 100%")
    print("-" * 70)
    
    resume3 = "JavaScript Python Java C++ React Node.js Django APIs DSA SQL MongoDB Git C++"
    result3 = calculate_match_percentage(resume3, "software")
    print("Resume: All 12 software skills")
    print("Category: Software Development")
    print("Total Skills:", result3["total_required_skills"])
    print("Matched:", result3["matched_skills"])
    print("MATCH PERCENTAGE:", result3["match_percentage"], "%")
    print("Expected: 100% (full match)")
    
    # Test Case 4: Web Dev partial
    print("\n" + "-" * 70)
    print("TEST 4: 4 out of 7 -> 57%")
    print("-" * 70)
    
    resume4 = "HTML CSS JavaScript Bootstrap"
    result4 = calculate_match_percentage(resume4, "web")
    print("Resume: HTML, CSS, JavaScript, Bootstrap")
    print("Category: Web Development")
    print("Total Skills:", result4["total_required_skills"])
    print("Matched:", result4["matched_skills"])
    print("MATCH PERCENTAGE:", result4["match_percentage"], "%")
    print("Expected: 57% (4/7)")
    
    # Test Case 5: With synonyms (js, py)
    print("\n" + "-" * 70)
    print("TEST 5: Using synonyms (js, py) -> 17%")
    print("-" * 70)
    
    resume5 = "JS Python"
    result5 = calculate_match_percentage(resume5, "software")
    print("Resume: JS, Python (using synonyms)")
    print("Category: Software Development")
    print("Total Skills:", result5["total_required_skills"])
    print("Matched:", result5["matched_skills"])
    print("MATCH PERCENTAGE:", result5["match_percentage"], "%")
    print("Expected: 17% (2/12)")
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print("Test 1 (6/12):", result1["match_percentage"], "% = 50%")
    print("Test 2 (Wrong):", result2["match_percentage"], "% = 0%")
    print("Test 3 (12/12):", result3["match_percentage"], "% = 100%")
    print("Test 4 (4/7):", result4["match_percentage"], "% = 57%")
    print("Test 5 (2/12):", result5["match_percentage"], "% = 17%")