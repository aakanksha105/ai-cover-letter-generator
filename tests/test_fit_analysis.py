from utils.utils import analyze_resume_job_fit, extract_catalog_skills, format_fit_summary_for_prompt


def test_skill_matching_detects_resume_overlap(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    resume = "Software engineer with Python, SQL, Flask, PostgreSQL, Docker, and REST API experience. Education and projects included. Experience building APIs."
    job = "Requirements: Build REST APIs using Python, SQL, Docker, AWS, and PostgreSQL. Experience with Flask preferred."

    fit = analyze_resume_job_fit(resume, job)

    assert "Python" in fit["matched_skills"]
    assert "SQL" in fit["matched_skills"]
    assert "AWS" in fit["missing_skills"]
    assert fit["fit_score"] > 0
    assert fit["requirement_lines"]


def test_extract_catalog_skills_avoids_plain_node_false_positive():
    text = "The user node in the graph stores metadata."
    skills = extract_catalog_skills(text)
    flattened = [skill for values in skills.values() for skill in values]
    assert "Node.js" not in flattened


def test_fit_summary_prompt_contains_missing_and_requirements():
    summary = format_fit_summary_for_prompt({
        "fit_score": 50,
        "matched_skills": ["Python"],
        "missing_skills": ["AWS"],
        "requirement_lines": ["Build APIs using Python and cloud services."],
    })
    assert "Keyword fit score: 50%" in summary
    assert "Python" in summary
    assert "AWS" in summary
    assert "Build APIs" in summary


def test_requirement_lines_skip_section_headings():
    from utils.utils import analyze_resume_job_fit

    job = """
    Required Qualifications
    2+ years of experience developing REST APIs with Python or Node.js.
    Preferred Qualifications
    Experience with SQL databases and cloud deployment is preferred.
    """
    resume = "Python REST APIs SQL cloud deployment"
    result = analyze_resume_job_fit(resume, job)
    lowered = [line.lower() for line in result["requirement_lines"]]

    assert "required qualifications" not in lowered
    assert "preferred qualifications" not in lowered
    assert any("rest apis" in line for line in lowered)


def test_dynamic_terms_do_not_include_generic_single_words(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    resume = "Python SQL APIs"
    job = "We need someone who can create, build, manage, and support teams in a fast paced environment."
    fit = analyze_resume_job_fit(resume, job)
    assert "create" not in [s.lower() for s in fit["job_skills_detected"]]
    assert "team" not in [s.lower() for s in fit["job_skills_detected"]]
