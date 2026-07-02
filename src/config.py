"""Project configuration."""

from pathlib import Path


class Config:
    """Central configuration used by Flask and the ranking pipeline."""

    BASE_DIR = Path(__file__).resolve().parent.parent
    DATA_DIR = BASE_DIR / "data"
    SAMPLE_DATA_DIR = BASE_DIR / "sample_data"
    UPLOAD_FOLDER = BASE_DIR / "uploads"
    OUTPUT_FOLDER = BASE_DIR / "outputs"
    SKILLS_CATALOG_PATH = DATA_DIR / "skills_catalog.json"

    ALLOWED_EXTENSIONS = {"pdf", "txt", "docx"}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
    SECRET_KEY = "replace-this-secret-key-before-production"

    DEFAULT_SCORING_METHOD = "hybrid"
    TFIDF_WEIGHT = 0.65
    SKILL_WEIGHT = 0.30
    EXPERIENCE_WEIGHT = 0.05
