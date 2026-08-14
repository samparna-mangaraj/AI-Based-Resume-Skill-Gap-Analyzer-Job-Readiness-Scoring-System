from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, JSON, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String(50), primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class JobCategory(Base):
    __tablename__ = "job_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    icon = Column(String(50))
    color = Column(String(20))
    description = Column(Text, nullable=True)
    
    # Relationships (Existing)
    skills = relationship("Skill", back_populates="category", cascade="all, delete-orphan")
    analyses = relationship("AnalysisResult", back_populates="category")
    
    # NEW: Extended Relationships
    roles = relationship("Role", back_populates="category", cascade="all, delete-orphan")
    certifications = relationship("Certification", back_populates="category", cascade="all, delete-orphan")
    master_recommendations = relationship("MasterRecommendation", back_populates="category", cascade="all, delete-orphan")

class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    category_id = Column(Integer, ForeignKey("job_categories.id"), index=True)
    
    category = relationship("JobCategory", back_populates="roles")

class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    tier = Column(String(20), nullable=False) # core, secondary, bonus
    category_id = Column(Integer, ForeignKey("job_categories.id"), index=True)
    
    category = relationship("JobCategory", back_populates="skills")

class Certification(Base):
    __tablename__ = "certifications"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    provider = Column(String(100))
    category_id = Column(Integer, ForeignKey("job_categories.id"), index=True)
    
    category = relationship("JobCategory", back_populates="certifications")

class MasterRecommendation(Base):
    __tablename__ = "master_recommendations"
    id = Column(Integer, primary_key=True, index=True)
    description = Column(Text, nullable=False)
    type = Column(String(50)) # skill_based, strategic
    skill_link = Column(String(100), nullable=True) # Optional link to a specific skill
    category_id = Column(Integer, ForeignKey("job_categories.id"), index=True)
    
    category = relationship("JobCategory", back_populates="master_recommendations")

class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)
    category_id = Column(Integer, ForeignKey("job_categories.id"), index=True)
    match_percentage = Column(Float)
    match_level = Column(String(50))
    matched_skills = Column(JSON)
    missing_skills = Column(JSON)
    recommendations = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    category = relationship("JobCategory", back_populates="analyses")
