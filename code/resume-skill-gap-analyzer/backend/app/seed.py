import pymysql
import os
import json
from dotenv import load_dotenv
from .database import SessionLocal, engine, Base
from .models import JobCategory, Skill, Role, Certification, MasterRecommendation

load_dotenv()

def create_database_if_not_exists():
    host = os.getenv("DB_HOST", "localhost")
    user = os.getenv("DB_USER", "root")
    password = os.getenv("DB_PASSWORD", "")
    db_name = os.getenv("DB_NAME", "skillgap_db")
    
    connection = pymysql.connect(host=host, user=user, password=password)
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        connection.commit()
    finally:
        connection.close()

def normalize_name(name: str) -> str:
    """Transformation Logic: Clean and normalize skill/entity names"""
    mapping = {
        "js": "JavaScript",
        "py": "Python",
        "k8s": "Kubernetes",
        "aws cloud": "AWS",
        "ml": "Machine Learning",
        "ai": "Artificial Intelligence"
    }
    name_clean = name.strip()
    return mapping.get(name_clean.lower(), name_clean)

def seed_database():
    # Only try to create MySQL database if we're not using SQLite
    if "sqlite" not in str(engine.url):
        create_database_if_not_exists()
        
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    if db.query(JobCategory).count() > 0:
        print("Existing data found. Updating schema additions...")
    
    # ── COMPLETE DATASET - ALL 15 CATEGORIES ────────────────────────
    CATEGORIES_DATA = {
        "Software Development": {
            "icon": "💻", "color": "#00f5ff",
            "roles": ["Backend Developer", "Frontend Developer", "Full Stack Engineer", "Software Engineer"],
            "skills": {"core": ["JavaScript", "Python", "Java", "C++", "React", "Node.js", "Django", "Spring Boot", "DSA", "OOP"], "secondary": ["SQL", "MongoDB", "APIs", "Git"], "bonus": ["Deployment", "System Design"]},
            "certifications": [("AWS Certified Developer", "AWS"), ("Oracle Java SE", "Oracle"), ("Meta Front-End Developer", "Meta")],
            "recommendations": ["Build a full-stack portfolio project", "Master Design Patterns", "Practice DSA on LeetCode", "Deploy projects on Vercel/AWS"]
        },
        "Web Development": {
            "icon": "🌐", "color": "#bf00ff",
            "roles": ["Web Developer", "UI Developer", "Web Designer"],
            "skills": {"core": ["HTML", "CSS", "JavaScript", "React", "Vue.js"], "secondary": ["Bootstrap", "Tailwind", "Responsive Design", "Figma"], "bonus": ["SEO", "WordPress"]},
            "certifications": [("Meta Front-End Developer", "Meta"), ("Google UX Design", "Google"), ("W3C HTML5 Certification", "W3C")],
            "recommendations": ["Create a stunning portfolio website", "Optimize page speed & Core Web Vitals", "Focus on UI attractiveness"]
        },
        "Mobile Development": {
            "icon": "📱", "color": "#00ff88",
            "roles": ["Android Developer", "iOS Developer", "Flutter Developer"],
            "skills": {"core": ["Kotlin", "Java", "Swift", "Flutter", "React Native"], "secondary": ["Firebase", "APIs", "SQLite", "REST"], "bonus": ["Push Notifications", "Authentication", "App Store Deployment"]},
            "certifications": [("Google Associate Android Developer", "Google"), ("Apple Certified iOS App", "Apple"), ("Flutter Developer Certification", "Google")],
            "recommendations": ["Publish at least 1 live app on Play Store", "Focus on smooth UI/UX", "Build apps with clean architecture"]
        },
        "UI/UX Design": {
            "icon": "🎨", "color": "#ff00a8",
            "roles": ["UI Designer", "UX Designer", "Product Designer"],
            "skills": {"core": ["Figma", "Adobe XD", "Sketch", "Wireframing"], "secondary": ["Prototyping", "User Research", "Design Principles", "Typography"], "bonus": ["Motion Design", "Design Systems", "Accessibility"]},
            "certifications": [("Google UX Design Certificate", "Google"), ("Certified UX Designer", "Interaction Design Foundation"), ("Adobe Certified Expert", "Adobe")],
            "recommendations": ["Build a strong portfolio on Dribbble", "Create detailed case studies", "Master Figma prototyping"]
        },
        "Data Science": {
            "icon": "📊", "color": "#0080ff",
            "roles": ["Data Analyst", "Data Scientist", "BI Developer"],
            "skills": {"core": ["Python", "R", "Statistics", "Machine Learning", "SQL"], "secondary": ["Pandas", "NumPy", "Tableau", "Power BI", "Excel"], "bonus": ["Deep Learning", "NLP", "Time Series"]},
            "certifications": [("Google Data Analytics Certificate", "Google"), ("IBM Data Science Professional", "IBM"), ("Microsoft Certified Data Analyst", "Microsoft")],
            "recommendations": ["Work on Kaggle datasets and competitions", "Build interactive dashboards", "Master statistical analysis"]
        },
        "AI/ML": {
            "icon": "🤖", "color": "#ff6b00",
            "roles": ["ML Engineer", "AI Engineer", "NLP Engineer"],
            "skills": {"core": ["Python", "TensorFlow", "PyTorch", "Machine Learning", "Deep Learning"], "secondary": ["NLP", "Computer Vision", "Scikit-learn", "Keras"], "bonus": ["MLOps", "Model Deployment", "Cloud ML"]},
            "certifications": [("TensorFlow Developer Certificate", "Google"), ("DeepLearning.AI TensorFlow Developer", "DeepLearning.AI"), ("AWS Machine Learning Specialty", "AWS")],
            "recommendations": ["Build end-to-end ML projects with deployment", "Learn model deployment using Flask/FastAPI", "Contribute to open source ML projects"]
        },
        "Cloud Computing": {
            "icon": "☁️", "color": "#00d4ff",
            "roles": ["Cloud Engineer", "Cloud Architect", "Solutions Architect"],
            "skills": {"core": ["AWS", "Azure", "GCP", "Cloud Architecture"], "secondary": ["Docker", "Kubernetes", "CI/CD", "Terraform"], "bonus": ["Serverless", "Cloud Security", "Cost Optimization"]},
            "certifications": [("AWS Solutions Architect Associate", "AWS"), ("Google Professional Cloud Architect", "GCP"), ("Microsoft Azure Administrator", "Microsoft")],
            "recommendations": ["Get AWS/Azure/GCP certifications", "Deploy real-world apps on cloud", "Learn Infrastructure as Code with Terraform"]
        },
        "Cybersecurity": {
            "icon": "🔒", "color": "#ff4444",
            "roles": ["Security Analyst", "Penetration Tester", "SOC Engineer"],
            "skills": {"core": ["Networking", "Cryptography", "Linux", "Security Fundamentals"], "secondary": ["Kali Linux", "Metasploit", "Firewalls", "SIEM"], "bonus": ["Penetration Testing", "Forensics", "Incident Response"]},
            "certifications": [("CompTIA Security+", "CompTIA"), ("Certified Ethical Hacker (CEH)", "EC-Council"), ("CISSP", "ISC2")],
            "recommendations": ["Practice on TryHackMe and HackTheBox", "Build a secure home lab", "Get CEH or CompTIA Security+"]
        },
        "Data Engineering": {
            "icon": "🗄️", "color": "#9b59b6",
            "roles": ["DBA", "Data Engineer", "ETL Developer"],
            "skills": {"core": ["SQL", "Database Design", "Python", "ETL"], "secondary": ["Hadoop", "Spark", "Kafka", "Airflow"], "bonus": ["Data Modeling", "Pipeline Optimization", "Cloud Data Warehouses"]},
            "certifications": [("Google Cloud Data Engineer", "Google"), ("AWS Data Analytics", "AWS"), ("Cloudera Certified Data Engineer", "Cloudera")],
            "recommendations": ["Master SQL deeply - window functions, CTEs", "Build end-to-end data pipelines with Airflow", "Learn Snowflake or BigQuery"]
        },
        "DevOps": {
            "icon": "⚙️", "color": "#27ae60",
            "roles": ["DevOps Engineer", "SRE", "Platform Engineer"],
            "skills": {"core": ["CI/CD", "Docker", "Kubernetes", "Jenkins"], "secondary": ["Bash", "Python", "Terraform", "Ansible"], "bonus": ["Prometheus", "Grafana", "Helm"]},
            "certifications": [("Kubernetes Administrator (CKA)", "CNCF"), ("AWS DevOps Engineer", "AWS"), ("Docker Certified Associate", "Docker")],
            "recommendations": ["Build CI/CD pipelines with GitHub Actions/Jenkins", "Automate infrastructure with Terraform", "Learn GitOps with ArgoCD"]
        },
        "IT Support": {
            "icon": "🌍", "color": "#e67e22",
            "roles": ["System Admin", "Network Engineer", "Help Desk"],
            "skills": {"core": ["Networking", "Linux", "Windows Server", "Active Directory"], "secondary": ["Troubleshooting", "VMware", "PowerShell"], "bonus": ["Security Basics", "Cloud Basics"]},
            "certifications": [("CompTIA A+", "CompTIA"), ("CompTIA Network+", "CompTIA"), ("CCNA", "Cisco")],
            "recommendations": ["Get CCNA certification", "Practice in virtual labs", "Learn PowerShell scripting"]
        },
        "Game Development": {
            "icon": "🎮", "color": "#e74c3c",
            "roles": ["Game Developer", "Unity Developer", "Unreal Developer"],
            "skills": {"core": ["Unity", "Unreal Engine", "C#", "C++"], "secondary": ["Game Physics", "3D Math", "Shader Programming"], "bonus": ["VR Development", "Multiplayer Networking"]},
            "certifications": [("Unity Certified Developer", "Unity"), ("Unreal Engine Certified Developer", "Epic Games")],
            "recommendations": ["Build at least 2 playable games", "Publish games on itch.io or Steam", "Master game physics and AI"]
        },
        "QA Testing": {
            "icon": "✅", "color": "#2ecc71",
            "roles": ["QA Engineer", "Automation Tester", "SDET"],
            "skills": {"core": ["Manual Testing", "Test Planning", "Bug Tracking"], "secondary": ["Selenium", "Cypress", "Playwright", "JUnit"], "bonus": ["API Testing", "Performance Testing", "Jira"]},
            "certifications": [("ISTQB Certified Tester", "ISTQB"), ("Certified Selenium Professional", "LambdaTest")],
            "recommendations": ["Learn automation testing frameworks", "Write proper test cases with edge cases", "Practice API testing with Postman"]
        },
        "Project Management": {
            "icon": "📋", "color": "#3498db",
            "roles": ["Project Manager", "Scrum Master", "Product Owner"],
            "skills": {"core": ["Agile", "Scrum", "Jira", "Trello"], "secondary": ["Risk Management", "Stakeholder Management", "Communication"], "bonus": ["PMP Certification", "Six Sigma"]},
            "certifications": [("PMP Certification", "PMI"), ("Certified Scrum Master (CSM)", "Scrum Alliance"), ("Google Project Management", "Google")],
            "recommendations": ["Manage small team projects", "Get Scrum Master certification", "Improve stakeholder communication"]
        },
        "Emerging Fields": {
            "icon": "🚀", "color": "#f39c12",
            "roles": ["Blockchain Developer", "AR/VR Developer", "IoT Engineer"],
            "skills": {"core": ["Solidity", "Web3", "Unity", "Embedded Systems"], "secondary": ["Smart Contracts", "XR Development", "IoT Protocols"], "bonus": ["DeFi", "NFTs", "Edge Computing"]},
            "certifications": [("Certified Blockchain Developer", "Blockchain Council"), ("Unity XR Developer", "Unity"), ("AWS IoT Core Certification", "AWS")],
            "recommendations": ["Pick ONE niche and specialize", "Build portfolio projects in your niche", "Contribute to Web3 open source"]
        }
    }

    try:
        for cat_name, data in CATEGORIES_DATA.items():
            category = db.query(JobCategory).filter(JobCategory.name == cat_name).first()
            if not category:
                category = JobCategory(name=cat_name, icon=data["icon"], color=data["color"])
                db.add(category)
                db.flush()

            # 1. Add Roles (Additive)
            current_roles = {r.name for r in category.roles}
            for role_name in data["roles"]:
                if role_name not in current_roles:
                    db.add(Role(name=role_name, category_id=category.id))

            # 2. Add Skills (Additive + Normalization)
            current_skills = {s.name.lower() for s in category.skills}
            for tier, skills in data["skills"].items():
                for s_name in skills:
                    normalized = normalize_name(s_name)
                    if normalized.lower() not in current_skills:
                        db.add(Skill(name=normalized, tier=tier, category_id=category.id))

            # 3. Add Certifications (Additive)
            current_certs = {c.name for c in category.certifications}
            for cert_name, provider in data["certifications"]:
                if cert_name not in current_certs:
                    db.add(Certification(name=cert_name, provider=provider, category_id=category.id))

            # 4. Add Recommendations (Additive)
            current_recs = {r.description for r in category.master_recommendations}
            for rec_desc in data["recommendations"]:
                if rec_desc not in current_recs:
                    db.add(MasterRecommendation(description=rec_desc, type="strategic", category_id=category.id))

        db.commit()
        print("Successfully integrated and refactored dataset with zero regression!")
    except Exception as e:
        db.rollback()
        print(f"Integration Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
