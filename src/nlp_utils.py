"""Reusable NLP cleaning utilities."""

from __future__ import annotations

import re
import unicodedata


def normalize_text(text: str) -> str:
    """Normalize resume/JD text while preserving important symbols such as C++, C#, and .NET."""
    if not text:
        return ""
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("\x00", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def clean_for_vectorizer(text: str) -> str:
    """Clean text for TF-IDF vectorization."""
    text = normalize_text(text).lower()
    text = re.sub(r"[^a-z0-9+#.\s-]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_years_of_experience(text: str) -> float:
    """Extract the strongest years-of-experience signal from free-form text.

    Examples detected:
    - 3 years of experience
    - 5+ yrs
    - experience: 2 years
    """
    if not text:
        return 0.0

    patterns = [
        r"(\d{1,2})\+?\s*(?:years|year|yrs|yr)\s*(?:of)?\s*(?:experience|exp)?",
        r"experience\s*[:\-]?\s*(\d{1,2})\+?\s*(?:years|year|yrs|yr)",
    ]
    years = []
    for pattern in patterns:
        years.extend(float(match) for match in re.findall(pattern, text.lower()))
    return max(years) if years else 0.0
