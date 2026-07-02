from pathlib import Path

from src.resume_parser import ResumeParser


def test_parse_txt_resume(tmp_path: Path):
    resume_file = tmp_path / "darshan_resume.txt"
    resume_file.write_text("Darshan Paapani\ndarshan@example.com\n+91 98765 43210\nPython NLP Flask", encoding="utf-8")

    parsed = ResumeParser().parse(resume_file)

    assert parsed["candidate_name"] == "Darshan Paapani"
    assert parsed["email"] == "darshan@example.com"
    assert "+91" in parsed["phone"]
    assert "Python" in parsed["text"]
