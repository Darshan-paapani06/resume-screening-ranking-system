from src.ranker import CandidateRanker


def test_ranker_orders_best_candidate_first():
    job_description = "Python SQL NLP TF-IDF embeddings Flask Docker machine learning"
    resumes = [
        {
            "filename": "frontend.txt",
            "candidate_name": "Frontend Candidate",
            "email": "front@example.com",
            "phone": "1234567890",
            "text": "JavaScript React CSS frontend design 5 years experience",
        },
        {
            "filename": "ml.txt",
            "candidate_name": "ML Candidate",
            "email": "ml@example.com",
            "phone": "1234567890",
            "text": "Python SQL NLP TF-IDF embeddings Flask Docker machine learning 3 years experience",
        },
    ]

    ranked = CandidateRanker().rank(job_description, resumes, method="hybrid")

    assert ranked[0]["candidate_name"] == "ML Candidate"
    assert ranked[0]["rank"] == 1
    assert ranked[0]["final_score"] > ranked[1]["final_score"]


def test_ranker_rejects_empty_job_description():
    try:
        CandidateRanker().rank("", [{"text": "Python"}], method="hybrid")
    except ValueError as exc:
        assert "Job description" in str(exc)
    else:
        raise AssertionError("Expected ValueError for empty job description")
