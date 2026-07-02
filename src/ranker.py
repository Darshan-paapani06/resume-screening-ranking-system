"""Candidate ranking engine using NLP similarity and skill matching."""

from __future__ import annotations

from typing import Dict, List

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.config import Config
from src.nlp_utils import clean_for_vectorizer, extract_years_of_experience
from src.skills import compare_skills, extract_skills


class CandidateRanker:
    """Rank resumes against a job description using TF-IDF and skill overlap."""

    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            max_features=5000,
            min_df=1,
        )

    def extract_job_skills(self, job_description: str):
        """Expose job skill extraction for routes and reporting."""
        return extract_skills(job_description)

    def rank(self, job_description: str, resumes: List[Dict[str, str]], method: str = "hybrid") -> List[dict]:
        """Rank resumes using tfidf, skills, or hybrid scoring.

        Args:
            job_description: Free-form job requirement text.
            resumes: Parsed resume dictionaries with text and metadata.
            method: "tfidf", "skills", or "hybrid".
        """
        if not job_description.strip():
            raise ValueError("Job description cannot be empty.")
        if not resumes:
            raise ValueError("At least one resume is required for ranking.")

        method = method.lower()
        if method not in {"tfidf", "skills", "hybrid"}:
            raise ValueError("method must be one of: tfidf, skills, hybrid")

        jd_clean = clean_for_vectorizer(job_description)
        resume_texts = [clean_for_vectorizer(resume.get("text", "")) for resume in resumes]
        tfidf_scores = self._calculate_tfidf_similarity(jd_clean, resume_texts)

        job_skills = extract_skills(job_description)
        ranked = []

        for resume, tfidf_score in zip(resumes, tfidf_scores):
            resume_text = resume.get("text", "")
            resume_skills = extract_skills(resume_text)
            matched_skills, missing_skills, skill_score = compare_skills(job_skills, resume_skills)
            years_experience = extract_years_of_experience(resume_text)
            experience_score = min(years_experience / 10.0, 1.0)

            final_score = self._combine_scores(
                tfidf_score=tfidf_score,
                skill_score=skill_score,
                experience_score=experience_score,
                method=method,
            )

            ranked.append(
                {
                    "rank": 0,
                    "filename": resume.get("filename", "Unknown"),
                    "candidate_name": resume.get("candidate_name", "Unknown"),
                    "email": resume.get("email", "Not Found"),
                    "phone": resume.get("phone", "Not Found"),
                    "final_score": round(final_score * 100, 2),
                    "tfidf_similarity": round(tfidf_score * 100, 2),
                    "skill_match_score": round(skill_score * 100, 2),
                    "experience_years": years_experience,
                    "experience_score": round(experience_score * 100, 2),
                    "matched_skills": sorted(matched_skills),
                    "missing_skills": sorted(missing_skills),
                    "recommendation": self._recommendation(final_score),
                    "resume_preview": resume_text[:350] + "..." if len(resume_text) > 350 else resume_text,
                }
            )

        ranked.sort(key=lambda item: item["final_score"], reverse=True)
        for index, candidate in enumerate(ranked, start=1):
            candidate["rank"] = index
        return ranked

    def _calculate_tfidf_similarity(self, job_description: str, resume_texts: List[str]) -> np.ndarray:
        documents = [job_description] + resume_texts
        matrix = self.vectorizer.fit_transform(documents)
        scores = cosine_similarity(matrix[0:1], matrix[1:]).flatten()
        return scores

    @staticmethod
    def _combine_scores(tfidf_score: float, skill_score: float, experience_score: float, method: str) -> float:
        if method == "tfidf":
            return float(tfidf_score)
        if method == "skills":
            return float(skill_score)
        return float(
            (Config.TFIDF_WEIGHT * tfidf_score)
            + (Config.SKILL_WEIGHT * skill_score)
            + (Config.EXPERIENCE_WEIGHT * experience_score)
        )

    @staticmethod
    def _recommendation(score: float) -> str:
        if score >= 0.75:
            return "Strong Match - Shortlist Immediately"
        if score >= 0.60:
            return "Good Match - Review Next"
        if score >= 0.40:
            return "Moderate Match - Keep as Backup"
        return "Low Match - Not Recommended"
