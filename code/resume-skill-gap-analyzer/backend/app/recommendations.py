from typing import List, Dict

class RecommendationEngine:
    """
    Expert Recommendation Engine
    Focus: Detailed, Project-Based Localized Advice for Technical Upskilling.
    """

    # Knowledge Base: Mapping of skills to detailed project-based advice
    # This acts as our localized 'Career Coach'
    SKILL_ADVICE: Dict[str, str] = {
        "python": "Master Python by building an automated Data Scraper or a Django-based web application. Focus on learning asynchronous programming and deep data structures.",
        "javascript": "Enhance your JS skills by building a complex real-time application using WebSockets or a custom State Management library. Deep dive into Event Loops and Closures.",
        "java": "Focus on Enterprise Java. Build a Microservice-based backend using Spring Boot and implement secure JWT authentication to understand scalable system architecture.",
        "react": "Go beyond basics by building a high-performance Dashboard with code-splitting and custom hooks. Master the Reconciliation algorithm and state optimization.",
        "docker": "Containerize a multi-service application (Frontend, Backend, DB). Focus on multi-stage builds and reducing image size for production-ready deployments.",
        "sql": "Develop a complex database schema for an e-commerce platform. Focus on query optimization, indexing strategies, and ACID compliance.",
        "aws": "Build a serverless application using AWS Lambda and S3. Understand cloud cost-optimization and Identity Access Management (IAM) policies.",
        "machine learning": "Build an End-to-End ML Pipeline—from data cleaning to model deployment. Focus on feature engineering and model evaluation metrics like Precision/Recall.",
        "figma": "Design a high-fidelity interactive prototype for a mobile app. Focus on Design Systems, auto-layouts, and accessibility standards (WCAG).",
        "kubernetes": "Orchestrate a cluster using Minikube. Practice horizontal scaling and liveness/readiness probes to ensure high availability.",
        "ci/cd": "Build a GitHub Actions or Jenkins pipeline that automates testing, linting, and deployment for a personal project.",
    }

    # Category-level professional pathways
    CATEGORY_ADVICE: Dict[str, str] = {
        "Software Development": "Prioritize System Design and Data Structures. Candidates who can articulate 'The Why' behind architectural choices stand out.",
        "Web Development": "Focus on performance and accessibility. Build a personal portfolio that showcases 90+ Lighthouse scores and real-world client UI flows.",
        "Data Science": "Bridge the gap between math and code. Build projects that solve real business problems, not just Kaggle competitions.",
        "Cybersecurity": "Develop a defensive mindset. Build and secure a home lab or participate in CTF (Capture The Flag) events to prove hands-on skill.",
        "DevOps": "Automation is everything. Focus on 'Infrastructure as Code' (Terraform) and site reliability Engineering (SRE) principles."
    }

    @classmethod
    def generate_detailed_recommendations(cls, missing_skills: List[str], category_name: str) -> List[dict]:
        """
        Generates structured, detailed recommendations for missing skills.
        """
        recommendations = []
        
        # 1. Provide Category-Level Strategic Advice
        strategic_advice = cls.CATEGORY_ADVICE.get(category_name, "Focus on building end-to-end projects that demonstrate your ability to solve complex problems independently.")
        recommendations.append({
            "type": "strategic",
            "title": f"Professional Path: {category_name}",
            "text": strategic_advice,
            "priority": "high"
        })

        # 2. Map Missing Skills to Detailed Project Advice
        # We limit to top 3-4 to avoid overwhelm
        for skill in missing_skills[:4]:
            skill_lower = skill.lower()
            advice = cls.SKILL_ADVICE.get(skill_lower, f"Build a comprehensive portfolio project that integrates {skill} to demonstrate your practical proficiency.")
            
            recommendations.append({
                "type": "skill_gap",
                "skill": skill,
                "title": f"Upskill in {skill}",
                "text": advice,
                "priority": "medium" if skill_lower not in ["python", "javascript", "java", "sql"] else "high"
            })

        return recommendations
