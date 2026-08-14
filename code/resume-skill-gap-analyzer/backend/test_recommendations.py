from app.recommendations import RecommendationEngine

def test_recommendation_logic():
    print("--- PERSONALIZED RECOMMENDATION TEST ---")
    
    # Simulating a Web Development profile with some common skill gaps
    missing_skills = ["Python", "Docker", "React", "SQL"]
    category = "Web Development"
    
    print(f"\nTarget Category: {category}")
    print(f"Detected Gaps: {', '.join(missing_skills)}")
    
    print("\n[Generated Career Roadmap]")
    recommendations = RecommendationEngine.generate_detailed_recommendations(missing_skills, category)
    
    for rec in recommendations:
        if rec["type"] == "strategic":
            print(f"\n[STRATEGIC ADVICE]: {rec['title']}")
            print(f"   Message: {rec['text']}")
        else:
            print(f"\n[SKILL GAP]: {rec['title']} (Priority: {rec['priority'].upper()})")
            print(f"   Advice: {rec['text']}")
            
    # Validation
    if len(recommendations) > 1:
        print("\n✅ RECOMMENDATION TEST PASSED: Structured roadmap generated.")
    else:
        print("\n❌ RECOMMENDATION TEST FAILED: No output generated.")

if __name__ == "__main__":
    test_recommendation_logic()
