import os
import json
from dotenv import load_dotenv
from app.database import SessionLocal, engine, Base
from app.models import JobCategory, Skill, Role, Certification, MasterRecommendation

load_dotenv()

FULL_DATASET = {
    "Software Development": {
        "icon": "💻",
        "roles": ["Frontend", "Backend", "Full Stack", "Software Engineer"],
        "core": ["javascript", "python", "java", "c++", "react", "node.js", "django", "spring boot", "dsa", "oop"],
        "secondary": ["sql", "mongodb", "apis", "git"],
        "bonus": ["deployment", "system design"],
        "certifications": [("AWS Certified Developer", "Amazon"), ("Certified Java Professional", "Oracle")],
        "recommendations": [
            "Build 3 real-world projects (e.g., SaaS, management systems)",
            "Practice DSA daily",
            "Deploy projects online",
            "Learn basic system design",
            "Master object-oriented programming principles"
        ]
    },
    "Web Development": {
        "icon": "🌐",
        "roles": ["Web Developer", "UI Developer", "Web Designer"],
        "core": ["html", "css", "javascript"],
        "secondary": ["bootstrap", "tailwind", "responsive design"],
        "bonus": ["seo"],
        "certifications": [("Cousera Meta Front-End", "Meta"), ("Google UX Professional", "Google")],
        "recommendations": [
            "Create a portfolio website",
            "Work with small businesses (real clients)",
            "Optimize speed & performance",
            "Focus on UI attractiveness"
        ]
    },
    "Mobile Development": {
        "icon": "📱",
        "roles": ["Android", "iOS", "Flutter Developer"],
        "core": ["kotlin", "java", "swift", "flutter", "react native"],
        "secondary": ["firebase", "apis"],
        "bonus": ["notifications", "authentication"],
        "certifications": [("Google Associate Android Developer", "Google"), ("Meta iOS Developer", "Meta")],
        "recommendations": [
            "Publish at least 1 live app on Play Store or App Store",
            "Learn authentication & notifications",
            "Focus on smooth UI/UX with fluid animations",
            "Add real-world features (payments, chat, etc.)"
        ]
    },
    "UI/UX Design": {
        "icon": "🎨",
        "roles": ["UI Designer", "UX Designer", "Product Designer"],
        "core": ["figma", "adobe xd"],
        "secondary": ["wireframing", "prototyping", "user research"],
        "bonus": ["design principles"],
        "certifications": [("Google UX Design Certificate", "Google"), ("Nielsen Norman Group UX Certification", "NN/g")],
        "recommendations": [
            "Create design case studies",
            "Redesign popular apps for practice",
            "Focus on user experience (psychology & usability)",
            "Build a strong portfolio"
        ]
    },
    "Data Science": {
        "icon": "🧠",
        "roles": ["Data Analyst", "Data Scientist"],
        "core": ["python", "r", "statistics"],
        "secondary": ["sql", "excel", "power bi", "tableau"],
        "bonus": ["machine learning"],
        "certifications": [("IBM Data Science Professional", "IBM"), ("Google Data Analytics Professional", "Google")],
        "recommendations": [
            "Work on Kaggle datasets",
            "Build interactive dashboards (Power BI / Tableau)",
            "Focus on insights, not just code",
            "Solve real business problems",
            "Learn storytelling with data"
        ]
    },
    "AI/ML": {
        "icon": "🤖",
        "roles": ["ML Engineer", "AI Engineer"],
        "core": ["python", "tensorflow", "pytorch"],
        "secondary": ["nlp", "deep learning"],
        "bonus": ["deployment"],
        "certifications": [("DeepLearning.AI TensorFlow Specialization", "DeepLearning.AI"), ("AWS Machine Learning Specialty", "AWS")],
        "recommendations": [
            "Build small ML projects first",
            "Learn model deployment (Flask / FastAPI)",
            "Use AI APIs in real apps",
            "Create AI-based SaaS tools",
            "Focus on practical use-cases"
        ]
    },
    "Cloud Computing": {
        "icon": "☁️",
        "roles": ["Cloud Engineer", "DevOps Engineer"],
        "core": ["aws", "azure", "gcp"],
        "secondary": ["docker", "kubernetes", "ci/cd"],
        "bonus": ["linux"],
        "certifications": [("AWS Cloud Practitioner", "AWS"), ("Azure Fundamentals (AZ-900)", "Microsoft")],
        "recommendations": [
            "Get cloud certifications (AWS/Azure/GCP)",
            "Deploy real projects on cloud platforms",
            "Learn containerization (Docker & Kubernetes)",
            "Understand scaling & cost optimization",
            "Study cloud architecture basics"
        ]
    },
    "Cybersecurity": {
        "icon": "🔐",
        "roles": ["Security Analyst", "Ethical Hacker"],
        "core": ["networking", "cryptography"],
        "secondary": ["kali linux", "metasploit"],
        "bonus": ["penetration testing"],
        "certifications": [("CompTIA Security+", "CompTIA"), ("Certified Ethical Hacker (CEH)", "EC-Council")],
        "recommendations": [
            "Practice on TryHackMe / Hack The Box",
            "Learn penetration testing",
            "Study real-world vulnerabilities",
            "Join bug bounty programs",
            "Build a security lab setup"
        ]
    },
    "Data Engineering": {
        "icon": "🗄️",
        "roles": ["DBA", "Data Engineer"],
        "core": ["sql", "database design"],
        "secondary": ["etl", "hadoop", "spark"],
        "bonus": ["optimization"],
        "certifications": [("Google Professional Data Engineer", "Google"), ("Azure Data Engineer Associate", "Microsoft")],
        "recommendations": [
            "Master advanced SQL (window functions, CTEs, optimization)",
            "Work with large datasets",
            "Build end-to-end ETL pipelines",
            "Optimize database performance",
            "Learn data warehousing"
        ]
    },
    "DevOps": {
        "icon": "🔄",
        "roles": ["DevOps Engineer", "SRE"],
        "core": ["ci/cd", "docker", "kubernetes"],
        "secondary": ["bash", "python"],
        "bonus": ["terraform"],
        "certifications": [("Certified Kubernetes Administrator (CKA)", "CNCF"), ("AWS Certified DevOps Engineer", "AWS")],
        "recommendations": [
            "Build CI/CD deployment pipelines",
            "Automate infrastructure provisioning & workflows",
            "Learn Docker & Kubernetes deeply",
            "Monitor applications (logs, metrics, alerts)",
            "Work on real DevOps projects"
        ]
    },
    "IT Support": {
        "icon": "🖥️",
        "roles": ["System Admin", "Network Engineer"],
        "core": ["networking", "linux", "windows"],
        "secondary": ["troubleshooting"],
        "bonus": ["security basics"],
        "certifications": [("CompTIA A+", "CompTIA"), ("Cisco Certified Network Associate (CCNA)", "Cisco")],
        "recommendations": [
            "Practice troubleshooting systems",
            "Learn Linux administration deeply",
            "Set up home lab environments",
            "Understand networking practically",
            "Gain hands-on experience"
        ]
    },
    "Game Development": {
        "icon": "🎮",
        "roles": ["Game Developer"],
        "core": ["unity", "unreal"],
        "secondary": ["c#", "c++"],
        "bonus": ["game physics"],
        "certifications": [("Unity Certified Associate", "Unity"), ("Unreal Engine Certificate", "Epic Games")],
        "recommendations": [
            "Build small playable games",
            "Focus on gameplay experience",
            "Learn physics & animations",
            "Publish games online (itch.io, Steam)",
            "Improve creativity & design skills"
        ]
    },
    "QA Testing": {
        "icon": "📊",
        "roles": ["QA Engineer", "Automation Tester"],
        "core": ["manual testing"],
        "secondary": ["selenium", "cypress"],
        "bonus": ["jira"],
        "certifications": [("ISTQB Certified Tester", "ISTQB"), ("Cypress Automation Course", "Udemy")],
        "recommendations": [
            "Learn both manual & automation testing",
            "Practice Selenium / Cypress / Playwright",
            "Write proper test cases with edge coverage",
            "Test real-world applications",
            "Understand the SDLC process"
        ]
    },
    "Project Management": {
        "icon": "🧾",
        "roles": ["Project Manager", "Scrum Master"],
        "core": ["agile", "scrum"],
        "secondary": ["jira", "trello"],
        "bonus": ["communication"],
        "certifications": [("Project Management Professional (PMP)", "PMI"), ("Certified Scrum Master (CSM)", "Scrum Alliance")],
        "recommendations": [
            "Learn Agile & Scrum methodologies",
            "Manage small projects/teams",
            "Improve communication & leadership skills",
            "Use tools like Jira/Trello effectively",
            "Handle real-world project scenarios"
        ]
    },
    "Emerging Fields": {
        "icon": "🧩",
        "roles": ["Blockchain Dev", "AR/VR Dev", "IoT Engineer"],
        "core": ["solidity", "web3", "embedded systems"],
        "secondary": ["unity"],
        "bonus": ["innovation"],
        "certifications": [("Certified Blockchain Developer", "Blockchain Council"), ("AWS IoT Specialization", "AWS")],
        "recommendations": [
            "Choose ONE niche and become a specialist",
            "Build 1–2 strong portfolio projects",
            "Stay updated with emerging trends",
            "Focus on innovation and practical use-cases"
        ]
    }
}  # <-- Removed the extra closing brace here

def seed_full():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    try:
        print("Finalizing expert recommendations for all 15 categories...")
        # Clear old recommendations to ensure exact match with user request
        db.query(MasterRecommendation).delete()
        
        for cat_name, data in FULL_DATASET.items():
            category = db.query(JobCategory).filter(JobCategory.name == cat_name).first()
            if not category:
                category = JobCategory(name=cat_name, icon=data["icon"], color="#00f5ff")
                db.add(category)
                db.flush()
            else:
                category.icon = data["icon"]
            
            # Sync Description
            base_desc = f"Professional requirements and benchmark standards for {cat_name}."
            rec_section = "\n\nRecommended Actions to Improve Eligibility:\n"
            for r_text in data["recommendations"]:
                rec_section += f"- {r_text}\n"
            category.description = base_desc + rec_section

            # Sync Roles
            current_roles = {r.name for r in category.roles}
            for role_name in data["roles"]:
                if role_name not in current_roles:
                    db.add(Role(name=role_name, category_id=category.id))

            # Sync Skills
            current_skills = {s.name.lower() for s in category.skills}
            def proc_sk(skills, tier):
                for s in skills:
                    if s.lower() not in current_skills:
                        db.add(Skill(name=s, tier=tier, category_id=category.id))
            proc_sk(data["core"], "core")
            proc_sk(data["secondary"], "secondary")
            proc_sk(data["bonus"], "bonus")

            # Sync Certifications
            current_certs = {c.name.lower() for c in category.certifications}
            for c_name, provider in data["certifications"]:
                if c_name.lower() not in current_certs:
                    db.add(Certification(name=c_name, provider=provider, category_id=category.id))

            # Sync Recommendations (Ensuring exact match)
            for r_text in data["recommendations"]:
                db.add(MasterRecommendation(description=r_text, type="strategic", category_id=category.id))

        db.commit()
        print("Database synchronized with exact expert recommendation set!")
    except Exception as e:
        db.rollback()
        print(f"Seeding Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_full()