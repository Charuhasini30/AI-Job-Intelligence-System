import logging
from typing import List, Dict, Tuple

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

class JobMatcher:
    """Match user skills with job requirements."""
    
    def __init__(self):
        """Initialize the job matcher."""
        if SKLEARN_AVAILABLE:
            try:
                self.vectorizer = TfidfVectorizer(
                    lowercase=True,
                    stop_words='english',
                    ngram_range=(1, 2),  # Include both unigrams and bigrams
                    max_features=5000
                )
                logging.info("Initialized TF-IDF vectorizer for job matching")
            except Exception as e:
                logging.warning(f"Failed to initialize TF-IDF vectorizer: {e}")
                self.vectorizer = None
        else:
            self.vectorizer = None
            logging.warning("scikit-learn not available, using basic keyword matching only")
    
    def calculate_keyword_match(self, user_skills: List[str], job_skills: List[str]) -> float:
        """Calculate match score based on keyword overlap."""
        user_skills_set = set(skill.lower().strip() for skill in user_skills)
        job_skills_set = set(skill.lower().strip() for skill in job_skills)
        
        if not job_skills_set:
            return 0.0
        
        # Calculate Jaccard similarity (intersection over union)
        intersection = user_skills_set.intersection(job_skills_set)
        union = user_skills_set.union(job_skills_set)
        
        jaccard_score = len(intersection) / len(union) if union else 0.0
        
        # Also calculate simple overlap ratio
        overlap_score = len(intersection) / len(job_skills_set)
        
        # Combine both scores with more weight on overlap
        combined_score = (overlap_score * 0.7) + (jaccard_score * 0.3)
        
        return min(combined_score, 1.0)
    
    def calculate_semantic_similarity(self, user_skills: List[str], job_skills: List[str]) -> float:
        """Calculate semantic similarity using TF-IDF and cosine similarity."""
        if not SKLEARN_AVAILABLE or self.vectorizer is None:
            # Fallback to simple keyword matching
            return self.calculate_keyword_match(user_skills, job_skills) * 0.5
        
        try:
            # Prepare text documents
            user_text = ' '.join(user_skills).lower()
            job_text = ' '.join(job_skills).lower()
            
            if not user_text.strip() or not job_text.strip():
                return 0.0
            
            # Create TF-IDF vectors
            documents = [user_text, job_text]
            tfidf_matrix = self.vectorizer.fit_transform(documents)
            
            # Calculate cosine similarity
            similarity_matrix = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
            similarity_score = similarity_matrix[0][0]
            
            return float(similarity_score)
            
        except Exception as e:
            logging.warning(f"Error calculating semantic similarity: {e}")
            return 0.0
    
    def find_missing_skills(self, user_skills: List[str], job_skills: List[str]) -> List[str]:
        """Find skills required by job but not present in user skills."""
        user_skills_lower = set(skill.lower().strip() for skill in user_skills)
        missing_skills = []
        
        for job_skill in job_skills:
            job_skill_lower = job_skill.lower().strip()
            if job_skill_lower not in user_skills_lower:
                # Check for partial matches (e.g., "react" matches "react.js")
                is_partial_match = any(
                    job_skill_lower in user_skill or user_skill in job_skill_lower
                    for user_skill in user_skills_lower
                )
                if not is_partial_match:
                    missing_skills.append(job_skill)
        
        return missing_skills
    
    def calculate_match_score(self, user_skills: List[str], job: Dict) -> float:
        """Calculate overall match score for a job."""
        job_skills = job.get('required_skills', [])
        
        if not job_skills:
            return 0.0
        
        # Calculate different similarity metrics
        keyword_score = self.calculate_keyword_match(user_skills, job_skills)
        semantic_score = self.calculate_semantic_similarity(user_skills, job_skills)
        
        # Weight the scores (keyword matching is more reliable for technical skills)
        final_score = (keyword_score * 0.8) + (semantic_score * 0.2)
        
        logging.debug(f"Job '{job.get('title', 'Unknown')}': "
                     f"keyword={keyword_score:.3f}, semantic={semantic_score:.3f}, "
                     f"final={final_score:.3f}")
        
        return final_score
    
    def get_recommendations(self, user_skills: List[str], jobs: List[Dict], top_n: int = 3) -> List[Tuple[Dict, float, List[str]]]:
        """Get top N job recommendations based on user skills."""
        if not user_skills:
            logging.warning("No user skills provided for matching")
            return []
        
        if not jobs:
            logging.warning("No jobs provided for matching")
            return []
        
        # Calculate match scores for all jobs
        job_scores = []
        for job in jobs:
            match_score = self.calculate_match_score(user_skills, job)
            missing_skills = self.find_missing_skills(user_skills, job.get('required_skills', []))
            job_scores.append((job, match_score, missing_skills))
        
        # Sort by match score (descending)
        job_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Return top N recommendations
        recommendations = job_scores[:top_n]
        
        logging.info(f"Generated {len(recommendations)} recommendations from {len(jobs)} jobs")
        for i, (job, score, missing) in enumerate(recommendations, 1):
            logging.info(f"  {i}. {job.get('title', 'Unknown')} - Score: {score:.3f}, "
                        f"Missing: {len(missing)} skills")
        
        return recommendations
    
    def calculate_ats_score(self, user_skills: List[str], job_skills: List[str], job_description: str = "") -> int:
        """
        Calculate ATS (Applicant Tracking System) score out of 100.
        This simulates how ATS systems evaluate resume-job compatibility.
        """
        if not job_skills:
            return 0
        
        user_skills_set = set(skill.lower().strip() for skill in user_skills)
        job_skills_set = set(skill.lower().strip() for skill in job_skills)
        
        # Basic skill matching (60% of score)
        skill_overlap = len(user_skills_set.intersection(job_skills_set))
        skill_match_ratio = skill_overlap / len(job_skills_set)
        skill_score = skill_match_ratio * 60
        
        # Bonus for having more skills than required (20% of score)
        extra_skills_bonus = min(len(user_skills_set) / len(job_skills_set), 2.0) * 20
        
        # Context matching from job description (20% of score)
        context_score = 0
        if job_description:
            description_lower = job_description.lower()
            context_matches = sum(1 for skill in user_skills if skill.lower() in description_lower)
            context_score = min(context_matches / len(user_skills), 1.0) * 20
        else:
            # If no description, give partial context score based on skill diversity
            context_score = min(len(user_skills_set) / 10, 1.0) * 20
        
        total_score = int(min(skill_score + extra_skills_bonus + context_score, 100))
        return max(total_score, 0)
