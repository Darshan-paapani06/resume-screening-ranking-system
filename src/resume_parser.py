"""Resume parsing utilities for TXT, PDF, and DOCX files."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict

from src.nlp_utils import normalize_text


class ResumeParser:
    """Parse resumes and extract candidate metadata."""

    def parse(self, file_path: str | Path) -> Dict[str, str]:
        """Parse a resume file and return text plus lightweight metadata."""
        path = Path(file_path)
        raw_text = self.extract_text(path)
        normalized_text = normalize_text(raw_text)

        return {
            "filename": path.name,
            "candidate_name": self.extract_candidate_name(raw_text, path.stem),
            "email": self.extract_email(normalized_text),
            "phone": self.extract_phone(normalized_text),
            "text": normalized_text,
        }

    def extract_text(self, path: Path) -> str:
        """Extract raw text from TXT, PDF, or DOCX."""
        suffix = path.suffix.lower()
        if suffix == ".txt":
            return path.read_text(encoding="utf-8", errors="ignore")
        if suffix == ".pdf":
            return self._extract_pdf_text(path)
        if suffix == ".docx":
            return self._extract_docx_text(path)
        raise ValueError(f"Unsupported file format: {suffix}")

    @staticmethod
    def _extract_pdf_text(path: Path) -> str:
        try:
            from pypdf import PdfReader
        except ImportError as exc:  # pragma: no cover - dependency guidance
            raise ImportError("Install pypdf to parse PDF resumes: pip install pypdf") from exc

        reader = PdfReader(str(path))
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(pages)

    @staticmethod
    def _extract_docx_text(path: Path) -> str:
        try:
            from docx import Document
        except ImportError as exc:  # pragma: no cover - dependency guidance
            raise ImportError("Install python-docx to parse DOCX resumes: pip install python-docx") from exc

        document = Document(str(path))
        return "\n".join(paragraph.text for paragraph in document.paragraphs)

    @staticmethod
    def extract_email(text: str) -> str:
        match = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
        return match.group(0) if match else "Not Found"

    @staticmethod
    def extract_phone(text: str) -> str:
        match = re.search(r"(?:\+?\d{1,3}[\s-]?)?(?:\(?\d{3,5}\)?[\s-]?)?\d{3,5}[\s-]?\d{4}", text)
        return match.group(0) if match else "Not Found"

    @staticmethod
    def extract_candidate_name(text: str, fallback: str) -> str:
        """Infer candidate name from the first meaningful line or fallback to file name."""
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            if "@" in line or any(token in line.lower() for token in ["resume", "curriculum", "phone", "email"]):
                continue
            words = re.findall(r"[A-Za-z]+", line)
            if 1 <= len(words) <= 4:
                return " ".join(word.capitalize() for word in words)
        return fallback.replace("_", " ").replace("-", " ").title()
