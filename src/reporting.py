"""Reporting helpers for ranked candidate output."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import List

import pandas as pd


def save_ranked_report(candidates: List[dict], output_folder: str | Path) -> str:
    """Save ranked candidates as a CSV report and return the file name."""
    output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)

    report_rows = []
    for candidate in candidates:
        report_rows.append(
            {
                "Rank": candidate["rank"],
                "Candidate Name": candidate["candidate_name"],
                "Email": candidate["email"],
                "Phone": candidate["phone"],
                "Final Score (%)": candidate["final_score"],
                "TF-IDF Similarity (%)": candidate["tfidf_similarity"],
                "Skill Match (%)": candidate["skill_match_score"],
                "Experience Years": candidate["experience_years"],
                "Recommendation": candidate["recommendation"],
                "Matched Skills": ", ".join(candidate["matched_skills"]),
                "Missing Skills": ", ".join(candidate["missing_skills"]),
                "Source File": candidate["filename"],
            }
        )

    filename = f"resume_ranking_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    pd.DataFrame(report_rows).to_csv(output_folder / filename, index=False)
    return filename
