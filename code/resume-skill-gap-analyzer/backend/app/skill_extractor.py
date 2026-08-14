import re
from typing import List, Set, Dict
from sqlalchemy.orm import Session
from .models import JobCategory, Skill

class SkillExtractor:
    """
    Expert NLP Skill Extraction Logic
    Strategy: Case-insensitive, Strict (Whole Word) matching using Regex Word Boundaries.
    """

    @staticmethod
    def get_all_skills_from_db(db: Session) -> Dict[str, str]:
        """
        Fetch all defined skills from MySQL to use as the master dictionary.
        Returns a mapping of skill_name_lowercase -> original_skill_name.
        """
        # We fetch from the 'skills' table we created during DB integration
        db_skills = db.query(Skill).all()
        
        # We use a dict to handle normalization and preserve original casing/naming
        master_skills = {}
        for s in db_skills:
            master_skills[s.name.lower()] = s.name
            
        return master_skills

    @staticmethod
    def extract(text: str, master_skills: Dict[str, str]) -> List[str]:
        """
        Extracts skills from text using Case-Insensitive, Strict-Word boundaries.
        Args:
            text: Cleaned resume text.
            master_skills: Dictionary of lowercase_skill -> display_name.
        """
        if not text:
            return []

        extracted_skills = set()
        
        # We iterate through the master skill list
        for skill_lower, display_name in master_skills.items():
            # NLP LOGIC: Case-insensitive + Strict (Word Boundaries)
            # \b ensures that 'Java' does not match 'JavaScript'
            # re.IGNORECASE handles the case insensitivity
            
            # Escape the skill name to handle special characters like C++, .NET, etc.
            escaped_skill = re.escape(skill_lower)
            
            # Special handling for C++ and C# which are often at word boundaries
            if skill_lower in ["c++", "cpp"]:
                pattern = r'(?i)(?:\b|(?<=\s))c\+\+(?:\b|(?=\s))'
            elif skill_lower in ["c#", "csharp"]:
                pattern = r'(?i)(?:\b|(?<=\s))c#(?:\b|(?=\s))'
            elif skill_lower == ".net":
                pattern = r'(?i)(?:\b|(?<=\s))\.net(?:\b|(?=\s))'
            else:
                pattern = fr'(?i)\b{escaped_skill}\b'
            
            if re.search(pattern, text):
                extracted_skills.add(display_name)
        
        # Return sorted list for consistent UI
        return sorted(list(extracted_skills))

    @classmethod
    def analyze_resume_skills(cls, cleaned_text: str, db: Session) -> Dict:
        """
        Wrapper to extract skills and group them by category for immediate feedback.
        """
        master_dict = cls.get_all_skills_from_db(db)
        found_skills = cls.extract(cleaned_text, master_dict)
        
        return {
            "found_count": len(found_skills),
            "skills": found_skills,
            "message": f"Successfully identified {len(found_skills)} industry-standard skills."
        }
