import os
import sys
from app.database import SessionLocal
from app.skill_extractor import SkillExtractor

def test_extraction():
    print("--- EXPERT SKILL EXTRACTION TEST ---")
    
    db = SessionLocal()
    try:
        # Sample Resume Text (Normalized lowercase as it would come from parser)
        sample_text = """
        senior software developer with expertise in java, c++, and python.
        working on cloud projects using aws and docker for deployment.
        frontend exposure to react and javascript.
        strong background in sql databases and git version control.
        also familiar with spring boot and django.
        """
        
        print("\n1. Running Extraction on Sample Technical Text...")
        result = SkillExtractor.analyze_resume_skills(sample_text, db)
        
        found = result["skills"]
        print(f"Skills Found ({len(found)}): {', '.join(found)}")
        
        # Validation checks
        critical_skills = ["Java", "C++", "Python", "AWS", "Docker", "React", "JavaScript", "SQL", "Git"]
        missing = [s for s in critical_skills if s.lower() not in [f.lower() for f in found]]
        
        if not missing:
            print("\n✅ ALL CRITICAL SKILLS IDENTIFIED!")
        else:
            print(f"\n❌ MISSING SKILLS: {', '.join(missing)}")
            
        # Strict boundary test
        print("\n2. Checking Strict Boundary (Java vs JavaScript)...")
        if "Java" in found and "JavaScript" in found:
            # Check if 'Java' is its own entry and not just a substring
            print("Successfully identified both 'Java' and 'JavaScript' as distinct skills.")
        else:
            print("Failed boundary check.")

    except Exception as e:
        print(f"Extraction Test Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_extraction()
