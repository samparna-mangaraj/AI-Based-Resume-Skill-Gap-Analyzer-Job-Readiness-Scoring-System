"""
Resume Routes
===========
Resume upload and management endpoints.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, status
from pydantic import BaseModel
from typing import Optional
import os
import uuid

from app.config import settings

router = APIRouter()


class ResumeResponse(BaseModel):
    id: str
    filename: str
    content: Optional[str] = None
    word_count: int = 0
    extracted_skills: list[str] = []
    metrics: dict = {}


import logging
logger = logging.getLogger(__name__)

@router.post("/upload", response_model=ResumeResponse)
async def upload_resume(resume: UploadFile = File(None)):
    """Upload resume file"""
    logger.info("Upload request received")
    try:
        if not resume:
            logger.warning("No file in request")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File not uploaded."
            )
        
        file = resume
        filename = file.filename
        logger.info(f"Uploading file: {filename}")
        
        # Validate file extension
        file_ext = os.path.splitext(filename)[1].lower()
        if file_ext not in settings.ALLOWED_EXTENSIONS:
            logger.warning(f"Unsupported file extension: {file_ext}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported format. Allowed: {settings.ALLOWED_EXTENSIONS}",
            )
        
        # Read file content
        content = await file.read()
        
        # Validate file size
        if len(content) > settings.MAX_FILE_SIZE:
            logger.warning(f"File too large: {len(content)} bytes")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File too large. Max size: {settings.MAX_FILE_SIZE / 1024 / 1024}MB",
            )
        
        # Store file correctly (local storage)
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        file_path = os.path.join(settings.UPLOAD_DIR, filename)
        with open(file_path, "wb") as f:
            f.write(content)
        logger.info(f"File saved to: {file_path}")

        # Extract and clean text using Professional Parser
        from app.parser import ResumeParser
        
        parsing_result = ResumeParser.parse(content, filename)
        logger.info(f"Parse result: success={parsing_result.get('success')}, word_count={parsing_result.get('word_count')}")
        
        if not parsing_result["success"]:
            logger.warning("Parsing failed")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Failed to extract meaningful text from the resume."
            )
        
        # 3. Identify Skills using Expert NLP Logic
        from app.skill_extractor import SkillExtractor
        from app.database import SessionLocal
        
        extracted_skills = []
        try:
            db = SessionLocal()
            extraction_result = SkillExtractor.analyze_resume_skills(parsing_result["cleaned_content"], db)
            extracted_skills = extraction_result["skills"]
            logger.info(f"Skill extraction found {len(extracted_skills)} skills")
        except Exception as e:
            # Log the error but continue without skills if database is not available
            logger.error(f"Skill extraction failed: {e}")
            extracted_skills = []
        finally:
            if 'db' in locals():
                db.close()
        
        # Generate unique ID
        resume_id = str(uuid.uuid4())
        logger.info(f"Returning response for {filename}")
        
        return ResumeResponse(
            id=resume_id,
            filename=filename,
            content=parsing_result["cleaned_content"],
            word_count=parsing_result["word_count"],
            extracted_skills=extracted_skills,
            metrics=parsing_result["metrics"]
        )
    except HTTPException as he:
        logger.error(f"HTTP error: {he.detail}")
        raise he
    except Exception as e:
        logger.error(f"Unexpected error in upload: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during resume processing. Please try again."
        )


@router.get("/{resume_id}", response_model=ResumeResponse)
async def get_resume(resume_id: str):
    """Get resume by ID"""
    # In production: retrieve from storage
    return ResumeResponse(
        id=resume_id,
        filename="resume.pdf",
        content="Sample resume content",
        word_count=150,
    )


@router.delete("/{resume_id}")
async def delete_resume(resume_id: str):
    """Delete resume"""
    # In production: delete from storage
    return {"message": f"Resume {resume_id} deleted"}