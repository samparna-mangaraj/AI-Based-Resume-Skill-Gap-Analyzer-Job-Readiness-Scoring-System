class ScoringSystem:
    """
    Expert Integrated Scoring System
    Formula: (Skill Match * 0.5) + (Semantic Fit * 0.5) + Heuristic Boost
    """

    @staticmethod
    def calculate_integrated_score(
        skill_match_pct: float, 
        semantic_score: float, 
        metrics: dict
    ) -> dict:
        """
        Computes a heavy-weight professional score.
        - skill_match_pct: 0-100 (from ScoringEngine)
        - semantic_score: 0-100 (from SemanticMatcher)
        - metrics: {'years_of_experience': int, 'project_count': int}
        """
        
        # 1. Base Weighted Score (50/50 split as requested)
        base_score = (skill_match_pct * 0.5) + (semantic_score * 0.5)
        
        # 2. Heuristic Boost (Experience & Projects)
        # We add up to 5 points for experience and 5 points for projects
        exp_boost = min(metrics.get("years_of_experience", 0) * 0.5, 5.0)
        proj_boost = min(metrics.get("project_count", 0) * 0.2, 5.0)
        
        total_boost = exp_boost + proj_boost
        
        # Final Score calculation
        final_score = base_score + total_boost
        
        # Ensure it stays within 0-100 range
        final_score = min(max(final_score, 0.0), 100.0)
        
        return {
            "final_score": round(final_score, 2),
            "breakdown": {
                "technical_weight": round(skill_match_pct * 0.5, 2),
                "semantic_weight": round(semantic_score * 0.5, 2),
                "professional_boost": round(total_boost, 2)
            },
            "metrics": metrics
        }

    @staticmethod
    def get_match_label(score: float) -> str:
        if score >= 90: return "🏆 Expert Level"
        if score >= 75: return "💪 Senior Match"
        if score >= 60: return "📈 Mid-Level Fit"
        if score >= 40: return "🌱 Junior / Entry"
        return "⚠️ Poor Alignment"
