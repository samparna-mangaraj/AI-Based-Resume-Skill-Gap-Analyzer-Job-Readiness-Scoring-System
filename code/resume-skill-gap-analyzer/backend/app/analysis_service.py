import logging
from sqlalchemy.orm import Session
from app.parser import ResumeParser
from app.skill_extractor import SkillExtractor
from app.semantic_engine import SemanticMatcher
from app.scoring_system import ScoringSystem
from app.recommendations import RecommendationEngine
from app.scoring_engine import analyze_resume as tech_score
from app.models import JobCategory, AnalysisResult

# Configure Detailed Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AnalysisService")

class AnalysisService:
    """
    Full-Stack Unified Analysis Service
    Workflow: Parse -> Extract -> ML Match -> Score -> Recommend
    """

    @staticmethod
    def run_full_analysis(db: Session, resume_text: str, category_id: int) -> dict:
        logger.info(f"--- Starting Full Analysis for Category ID: {category_id} ---")

        # 1. Fetch Category Definition
        category = db.query(JobCategory).filter(JobCategory.id == category_id).first()
        if not category:
            logger.error("Category not found")
            return {"error": "Category not found"}

        # 2. Expert Skill Extraction
        logger.info("Step 2: Performing Expert Skill Extraction...")
        extraction_result = SkillExtractor.analyze_resume_skills(resume_text, db)
        matched_skills = extraction_result["skills"]
        logger.info(f"Extracted {len(matched_skills)} industry skills.")

        # 3. Technical Strategy Scoring (Weighted Tiers)
        logger.info("Step 3: Calculating Technical Weighted Match...")
        # (Internal logic uses the tiered engine)
        tech_results = tech_score(resume_text, category.name.lower().replace(" ", ""), 0) 
        skill_match_pct = tech_results["skill_match_percentage"]
        missing_skills = tech_results["missing_skills"]

        # 4. ML Semantic Similarity
        logger.info("Step 4: Executing ML Semantic Similarity Engine...")
        matcher = SemanticMatcher()
        category_context = SemanticMatcher.get_category_context({
            "name": category.name,
            "core": [s.name for s in category.skills if s.tier == "core"],
            "secondary": [s.name for s in category.skills if s.tier == "secondary"],
            "bonus": [s.name for s in category.skills if s.tier == "bonus"]
        })
        semantic_score = matcher.calculate_similarity(resume_text, category_context)
        logger.info(f"Semantic Domain Alignment: {semantic_score}%")

        # 5. Extraction of Career Metrics (Boosts)
        logger.info("Step 5: Extracting Professional Metrics...")
        metrics = ResumeParser.extract_metrics(resume_text)
        logger.info(f"Found {metrics['years_of_experience']}y experience and {metrics['project_count']} projects.")

        # 6. Integrated Scoring System
        logger.info("Step 6: Integrating Final Scores...")
        final_result = ScoringSystem.calculate_integrated_score(
            skill_match_pct,
            semantic_score,
            metrics
        )
        logger.info(f"Final Integrated Score: {final_result['final_score']}%")

        # 7. Personalized Career Roadmap
        logger.info("Step 7: Generating Personalized Recommendations...")
        recommendations = RecommendationEngine.generate_detailed_recommendations(
            missing_skills,
            category.name
        )

        # 8. Persistence (Save to MySQL)
        logger.info("Step 8: Persisting Result to Database...")
        db_result = AnalysisResult(
            category_id=category.id,
            match_percentage=final_result["final_score"],
            match_level=ScoringSystem.get_match_label(final_result["final_score"]),
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            recommendations=recommendations
        )
        db.add(db_result)
        db.commit()
        db.refresh(db_result)

        # 9. Return Standard JSON
        return {
            "analysis_id": db_result.id,
            "category": category.name,
            "match_percentage": final_result["final_score"],
            "match_level": db_result.match_level,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "recommendations": recommendations,
            "metrics": metrics
        }
