from app.scoring_system import ScoringSystem

def test_scoring_logic():
    print("--- INTEGRATED SCORING SYSTEM TEST ---")
    
    # Baseline: Two candidates with identical skill and semantic scores
    # but different professional experience levels.
    
    skill_pct = 80.0    # 80% Keyword Match
    semantic = 70.0     # 70% Semantic Fit
    
    # Candidate A: Senior (10 years, 20 projects)
    metrics_a = {"years_of_experience": 10, "project_count": 20}
    
    # Candidate B: Junior (0 years, 0 projects)
    metrics_b = {"years_of_experience": 0, "project_count": 0}
    
    print(f"\nBaseline: {skill_pct}% Skills, {semantic}% Semantic Fit")
    
    result_a = ScoringSystem.calculate_integrated_score(skill_pct, semantic, metrics_a)
    result_b = ScoringSystem.calculate_integrated_score(skill_pct, semantic, metrics_b)
    
    print("\n[Candidate A - Senior]")
    print(f"Final Score: {result_a['final_score']}%")
    print(f"Label: {ScoringSystem.get_match_label(result_a['final_score']).encode('ascii', 'ignore').decode()}")
    print(f"Breakdown: {result_a['breakdown']}")
    
    print("\n[Candidate B - Junior]")
    print(f"Final Score: {result_b['final_score']}%")
    print(f"Label: {ScoringSystem.get_match_label(result_b['final_score']).encode('ascii', 'ignore').decode()}")
    print(f"Breakdown: {result_b['breakdown']}")
    
    # Validation
    delta = result_a['final_score'] - result_b['final_score']
    print(f"\nProfessional Delta: +{delta}% score boost based on Experience/Projects.")
    
    if delta > 0:
        print("\n[SUCCESS] Scoring system correctly identifies and boosts experienced profiles.")
    else:
        print("\n[FAILED] Scoring system is ignoring professional metrics.")

if __name__ == "__main__":
    test_scoring_logic()
