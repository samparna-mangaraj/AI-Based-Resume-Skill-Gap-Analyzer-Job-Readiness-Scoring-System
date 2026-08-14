from app.semantic_engine import SemanticMatcher

def test_semantic_matching():
    print("--- ML SEMANTIC SIMILARITY TEST ---")
    
    matcher = SemanticMatcher()
    
    # Define an "Ideal Profile" for Data Science
    data_science_ideal = SemanticMatcher.get_category_context({
        "name": "Data Science",
        "core": ["python", "statistics", "machine learning", "r"],
        "secondary": ["sql", "tableau", "pandas"],
        "bonus": ["deep learning", "nlp"]
    })
    
    # Test 1: Highly relevant resume
    resume_ds = """
    experienced data scientist proficient in python and statistical modeling.
    implemented machine learning pipelines and performed data visualization using tableau.
    comfortable with sql and predictive analytics.
    """
    
    # Test 2: Irrelevant resume (Web Developer)
    resume_web = """
    senior frontend architect specializing in react and modern javascript.
    deep expertise in bootstrap, css, and building responsive user interfaces.
    familiar with node.js and rest api design.
    """
    
    print(f"\nComparing against Ideal Profile: Data Science")
    
    score1 = matcher.calculate_similarity(resume_ds, data_science_ideal)
    print(f"Test 1 (Relevant DS Resume) -> Semantic Score: {score1}%")
    
    score2 = matcher.calculate_similarity(resume_web, data_science_ideal)
    print(f"Test 2 (Irrelevant Web Resume) -> Semantic Score: {score2}%")
    
    # Validation
    if score1 > score2:
        print("\n✅ ML VALIDATION PASSED: Correctly identified relevant profile with higher score.")
    else:
        print("\n❌ ML VALIDATION FAILED: Similarity logic is not distinguishing between contexts.")

if __name__ == "__main__":
    test_semantic_matching()
