import pytest

pytest.importorskip("streamlit")

from app import extract_resume_contact_details, recommended_emphasis


def test_extract_resume_contact_details_finds_common_header_fields():
    resume = """
    Jane Doe
    jane@example.com | (555) 123-4567
    linkedin.com/in/janedoe | github.com/janedoe
    Experience
    Built Python APIs and SQL dashboards.
    """
    details = extract_resume_contact_details(resume)

    assert details["name"] == "Jane Doe"
    assert details["email"] == "jane@example.com"
    assert "555" in details["phone"]
    assert details["linkedin"].lower().endswith("linkedin.com/in/janedoe")
    assert details["portfolio"].lower().endswith("github.com/janedoe")


def test_recommended_emphasis_uses_matched_skills_and_short_requirements():
    fit = {
        "matched_skills": ["Python", "SQL", "Docker", "REST API", "React"],
        "requirement_lines": [
            "Build REST APIs using Python and SQL.",
            "This requirement line is intentionally extremely long and should not be included because it is over the UI-friendly limit for recommended emphasis text and would clutter the page with too much content."
        ],
    }

    emphasis = recommended_emphasis(fit)

    assert emphasis[:4] == ["Python", "SQL", "Docker", "REST API"]
    assert "Build REST APIs using Python and SQL." in emphasis
