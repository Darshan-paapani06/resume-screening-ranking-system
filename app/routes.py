"""Web routes for the resume ranking application."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import List

from flask import Blueprint, current_app, render_template, request, send_from_directory, flash, redirect, url_for
from werkzeug.utils import secure_filename

from src.config import Config
from src.ranker import CandidateRanker
from src.resume_parser import ResumeParser
from src.reporting import save_ranked_report

main_bp = Blueprint("main", __name__)


def _allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in Config.ALLOWED_EXTENSIONS


@main_bp.route("/", methods=["GET"])
def index():
    """Render the home page."""
    return render_template("index.html")


@main_bp.route("/health", methods=["GET"])
def health():
    """Lightweight health check for deployment platforms."""
    return {"status": "ok", "service": "resume-screening-ranking-system"}


@main_bp.route("/rank", methods=["POST"])
def rank_resumes():
    """Parse uploaded resumes, rank them, and display the final candidate report."""
    job_description = request.form.get("job_description", "").strip()
    scoring_method = request.form.get("scoring_method", "hybrid")
    uploaded_files = request.files.getlist("resumes")

    if not job_description:
        flash("Please paste a job description before ranking candidates.", "error")
        return redirect(url_for("main.index"))

    valid_files = [file for file in uploaded_files if file and _allowed_file(file.filename)]
    if not valid_files:
        flash("Please upload at least one PDF, TXT, or DOCX resume.", "error")
        return redirect(url_for("main.index"))

    parser = ResumeParser()
    resumes: List[dict] = []
    failed_files: List[str] = []

    for file in valid_files:
        safe_name = secure_filename(file.filename)
        saved_path = Path(current_app.config["UPLOAD_FOLDER"]) / f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{safe_name}"
        file.save(saved_path)

        try:
            parsed = parser.parse(saved_path)
            if parsed["text"]:
                resumes.append(parsed)
            else:
                failed_files.append(safe_name)
        except Exception as exc:  # noqa: BLE001 - app should continue processing other resumes
            failed_files.append(f"{safe_name} ({exc})")

    if not resumes:
        flash("None of the uploaded resumes could be parsed. Try TXT files first, then PDFs/DOCX.", "error")
        return redirect(url_for("main.index"))

    ranker = CandidateRanker()
    ranked_candidates = ranker.rank(job_description=job_description, resumes=resumes, method=scoring_method)

    report_filename = save_ranked_report(ranked_candidates, current_app.config["OUTPUT_FOLDER"])

    return render_template(
        "results.html",
        candidates=ranked_candidates,
        scoring_method=scoring_method,
        report_filename=report_filename,
        failed_files=failed_files,
        job_skill_count=len(ranker.extract_job_skills(job_description)),
    )


@main_bp.route("/download/<path:filename>", methods=["GET"])
def download_report(filename: str):
    """Download a generated CSV report."""
    return send_from_directory(current_app.config["OUTPUT_FOLDER"], filename, as_attachment=True)
