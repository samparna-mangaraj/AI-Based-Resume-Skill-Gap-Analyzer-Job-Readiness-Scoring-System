from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import JobCategory, Skill
from PyPDF2 import PdfReader
import io
import re

router = APIRouter()

def clean_text(text: str) -> str:
    """Normalize text: lowercase and remove punctuation"""
    text = text.lower()
    text = re.sub(r'[^\w\s]', ' ', text)
    return " ".join(text.split())

@router.get("/categories")
async def get_categories(db: Session = Depends(get_db)):
    """Fetch all job categories with icons and colors"""
    from sqlalchemy.orm import joinedload
    categories = db.query(JobCategory).options(
        joinedload(JobCategory.roles),
        joinedload(JobCategory.skills),
        joinedload(JobCategory.certifications),
        joinedload(JobCategory.master_recommendations)
    ).all()

    return {
        "categories": [
            {
                "id": cat.id,
                "name": cat.name,
                "icon": cat.icon,
                "color": cat.color,
                "description": cat.description,
                "roles": [r.name for r in (cat.roles or [])],
                "skills": {
                    "core": [s.name for s in cat.skills if s.tier == "core"],
                    "secondary": [s.name for s in cat.skills if s.tier == "secondary"],
                    "bonus": [s.name for s in cat.skills if s.tier == "bonus"]
                },
                "recommendations": {rec.skill_link or f"Strategy_{rec.id}": rec.description for rec in cat.master_recommendations},
                "certifications": [{"name": c.name, "provider": c.provider} for c in cat.certifications]
            } for cat in categories
        ]
    }

@router.post("/analyze")
async def analyze_resume(
    resume: UploadFile = File(...),
    job_description: UploadFile = File(...),  # Make job description required
    db: Session = Depends(get_db)
):
    """
    STRICT End-to-End Integration API
    Formula: match_percentage = (matched_count / total_skills) * 100
    """
    
    # 1. Validate File
    if not resume.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported for strict analysis.")

    # 2. Extract Text from Resume PDF
    try:
        content = await resume.read()
        pdf_file = io.BytesIO(content)
        reader = PdfReader(pdf_file)
        raw_text = ""
        for page in reader.pages:
            raw_text += page.extract_text() + " "
        
        if not raw_text.strip():
            raise ValueError("Empty or unreadable PDF content.")
            
        cleaned_resume_text = clean_text(raw_text)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"PDF Parsing Failed: {str(e)}")

    # 3. Extract Text from Job Description PDF (if provided)
    job_desc_text = ""
    if job_description:
        try:
            content_jd = await job_description.read()
            pdf_file_jd = io.BytesIO(content_jd)
            reader_jd = PdfReader(pdf_file_jd)
            raw_text_jd = ""
            for page in reader_jd.pages:
                raw_text_jd += page.extract_text() + " "
            
            if raw_text_jd.strip():
                job_desc_text = clean_text(raw_text_jd)
        except Exception as e:
            # If job description extraction fails, log and continue without it
            print(f"Warning: Job description extraction failed: {e}")

    # 4. Determine target skills
    if job_desc_text:
        # Extract skills from job description text by matching against all known skills
        # First, get all skill names and clean them (lowercase, remove punctuation)
        all_skills = db.query(Skill.name).all()
        cleaned_skills = [clean_text(skill_name) for (skill_name,) in all_skills]
        # Find skills that appear in the cleaned job description text
        target_skills = [skill for skill in cleaned_skills if skill in job_desc_text]
    else:
        # Fallback: Return an error if no job description provided
        raise HTTPException(status_code=400, detail="Job description is required for analysis.")

    if not target_skills:
        # No skills found in job description
        raise HTTPException(status_code=422, detail="Could not extract any skills from job description.")

    # 5. Matching Logic
    matched_skills = []
    for skill in target_skills:
        if skill in cleaned_resume_text:
            matched_skills.append(skill)
    
    matched_skills = sorted(list(set(matched_skills)))
    missing_skills = [s for s in target_skills if s not in matched_skills]

    # 6. Score Calculation
    matched_count = len(matched_skills)
    total_skills = len(target_skills)
    match_percentage = (matched_count / total_skills) * 100 if total_skills > 0 else 0

    # Determine match level, color, and emoji
    if match_percentage >= 75:
        match_level = "Strong"
        match_color = "#00ff88"
        match_emoji = "🏆"
    elif match_percentage >= 40:
        match_level = "Moderate"
        match_color = "#00f5ff"
        match_emoji = "📈"
    else:
        match_level = "Weak"
        match_color = "#ff4444"
        match_emoji = "⚠️"

    # 7. Fetch Recommendations and Certifications from DB
    recs = []
    
    # 8. Add specific "Course Adaption" recommendation if needed
    # (This part might need adjustment since we're not using category-specific certs)
    # For now, skip this or provide generic recommendation

    # 6c. Standard Recommendations from DB
    # We need to find recommendations that match missing skills
    # Since we don't have a specific category, we can find recommendations for any skill
    # For simplicity, provide a simple recommendation based on missing skills
    
    if missing_skills:
        recs.append({
            "key": "Skill Focus",
            "text": f"Focus on mastering: {', '.join(missing_skills[:5])}. These skills are in high demand for the job you're targeting.",
            "priority": "high"
        })
    else:
        recs.append({
            "key": "Excellent Match",
            "text": "Congratulations! Your resume matches all the required skills for this job.",
            "priority": "high"
        })

    # 9. Return Results
    return {
        "category": "Job Description Match",
        "roles": ["Job Seeker"],
        "icon": "🎯",
        "match_percentage": round(match_percentage, 2),
        "match_level": "Strong" if match_percentage >= 75 else "Moderate" if match_percentage >= 40 else "Weak",
        "match_color": "#00ff88" if match_percentage >= 75 else "#00f5ff" if match_percentage >= 40 else "#ff4444",
        "match_emoji": "🏆" if match_percentage >= 75 else "📈" if match_percentage >= 40 else "⚠️",
        "total_skills": total_skills,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "recommendations": recs,
        "certifications": [],
        "best_role": "Job Seeker",
        "best_category": "Job Description Match",
        "mode": "job_description"
    }