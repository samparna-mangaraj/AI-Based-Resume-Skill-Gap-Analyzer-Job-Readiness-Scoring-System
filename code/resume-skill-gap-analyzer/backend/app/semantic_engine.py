from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List

class SemanticMatcher:
    """
    Expert ML-driven Semantic Similarity Engine
    Algorithm: TF-IDF (Term Frequency-Inverse Document Frequency)
    Metric: Cosine Similarity
    Optimized for: High Accuracy (using Bigrams)
    """

    def __init__(self):
        # We use a 1-2 gram range (Unigrams + Bigrams) for context preservation
        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 2), # Capture context like "full stack" or "machine learning"
            max_features=5000
        )

    def calculate_similarity(self, resume_text: str, category_description: str) -> float:
        """
        Calculates the semantic distance between a resume and a job category.
        Returns a score between 0.0 and 100.0.
        """
        if not resume_text or not category_description:
            return 0.0

        try:
            # Combine documents into a corpus for the vectorizer
            corpus = [resume_text, category_description]
            
            # Fit and transform the corpus
            tfidf_matrix = self.vectorizer.fit_transform(corpus)
            
            # Compute Cosine Similarity between document 0 (resume) and document 1 (category)
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
            
            # Extract the raw float value and convert to percentage
            score = float(similarity[0][0]) * 100
            
            # Normalize: TF-IDF on short texts often yields low raw cosine scores.
            # We apply a slight logarithmic boost for better human readability if the score is > 0.
            if score > 0:
                score = min(score * 1.5, 100.0) # Heuristic boost for resume/job matching

            return round(score, 2)

        except Exception as e:
            print(f"ML Processing Error: {e}")
            return 0.0

    @staticmethod
    def get_category_context(category_data: dict) -> str:
        """
        Synthesizes an 'Ideal Profile' string from category skills and metadata.
        This provides a rich semantic target for the comparison.
        """
        skills = []
        if "core" in category_data: skills.extend(category_data["core"])
        if "secondary" in category_data: skills.extend(category_data["secondary"])
        if "bonus" in category_data: skills.extend(category_data["bonus"])
        
        # Build a robust target string
        context = f"Professional expertise in {', '.join(skills)}. "
        context += "Utilizing industry standard tools and methodologies to achieve project goals. "
        context += f"Highly proficient in technical competencies related to {category_data.get('name', 'this field')}."
        
        return context.lower()
