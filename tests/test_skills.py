from src.skills import compare_skills, extract_skills


def test_extract_skills_detects_core_terms():
    text = "Python SQL NLP TF-IDF embeddings Flask Docker and scikit-learn"
    skills = extract_skills(text)
    assert "python" in skills
    assert "sql" in skills
    assert "nlp" in skills
    assert "tf-idf" in skills
    assert "flask" in skills
    assert "docker" in skills
    assert "scikit-learn" in skills


def test_compare_skills_returns_score():
    job = {"python", "sql", "docker"}
    resume = {"python", "docker"}
    matched, missing, score = compare_skills(job, resume)
    assert matched == {"python", "docker"}
    assert missing == {"sql"}
    assert round(score, 2) == 0.67
