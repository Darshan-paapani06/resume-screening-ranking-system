"""Skill catalog loading and skill extraction helpers."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, Iterable, List, Set, Tuple

from src.config import Config
from src.nlp_utils import normalize_text


DEFAULT_SKILL_CATALOG: Dict[str, List[str]] = {
    "Programming Languages": ["python", "sql", "java", "javascript", "c++", "c#", "r", "scala"],
    "Machine Learning": [
        "machine learning",
        "deep learning",
        "supervised learning",
        "unsupervised learning",
        "classification",
        "regression",
        "clustering",
        "xgboost",
        "random forest",
        "logistic regression",
        "scikit-learn",
        "sklearn",
    ],
    "Data Engineering": ["pandas", "numpy", "spark", "hadoop", "etl", "airflow", "data pipeline"],
    "NLP": ["nlp", "natural language processing", "spacy", "nltk", "transformers", "bert", "tf-idf", "embeddings"],
    "Cloud & MLOps": ["docker", "kubernetes", "aws", "azure", "gcp", "mlflow", "fastapi", "flask", "streamlit", "ci/cd"],
    "Databases": ["mysql", "postgresql", "mongodb", "redis", "snowflake", "bigquery"],
    "Analytics": ["power bi", "tableau", "excel", "statistics", "a/b testing", "dashboard", "visualization"],
    "Soft Skills": ["communication", "leadership", "stakeholder", "problem solving", "collaboration"],
}


def load_skill_catalog(path: Path | None = None) -> Dict[str, List[str]]:
    """Load a skill catalog from JSON or fallback to a built-in catalog."""
    path = path or Config.SKILLS_CATALOG_PATH
    if path.exists():
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    return DEFAULT_SKILL_CATALOG


def flatten_skills(catalog: Dict[str, List[str]]) -> List[str]:
    """Flatten category-based skills into a sorted unique list."""
    skills = {skill.strip().lower() for values in catalog.values() for skill in values}
    return sorted(skills, key=len, reverse=True)


def _skill_pattern(skill: str) -> re.Pattern:
    escaped = re.escape(skill.lower())
    # Use custom boundaries so C++, C#, .NET, and hyphenated skills still work.
    return re.compile(rf"(?<![a-z0-9+#.]){escaped}(?![a-z0-9+#.])", re.IGNORECASE)


def extract_skills(text: str, catalog: Dict[str, List[str]] | None = None) -> Set[str]:
    """Extract known skills from text using a curated skill catalog."""
    if not text:
        return set()

    catalog = catalog or load_skill_catalog()
    normalized = normalize_text(text).lower()
    detected = set()

    for skill in flatten_skills(catalog):
        if _skill_pattern(skill).search(normalized):
            canonical = "scikit-learn" if skill == "sklearn" else skill
            detected.add(canonical)

    return detected


def categorize_detected_skills(skills: Iterable[str], catalog: Dict[str, List[str]] | None = None) -> Dict[str, List[str]]:
    """Group extracted skills by category for dashboard display."""
    catalog = catalog or load_skill_catalog()
    skill_set = {skill.lower() for skill in skills}
    categorized: Dict[str, List[str]] = {}

    for category, category_skills in catalog.items():
        matches = []
        for skill in category_skills:
            canonical = "scikit-learn" if skill.lower() == "sklearn" else skill.lower()
            if canonical in skill_set:
                matches.append(canonical)
        if matches:
            categorized[category] = sorted(set(matches))

    return categorized


def compare_skills(job_skills: Set[str], resume_skills: Set[str]) -> Tuple[Set[str], Set[str], float]:
    """Return matched skills, missing skills, and skill match score."""
    if not job_skills:
        return set(), set(), 0.0

    matched = job_skills.intersection(resume_skills)
    missing = job_skills.difference(resume_skills)
    score = len(matched) / len(job_skills)
    return matched, missing, score
