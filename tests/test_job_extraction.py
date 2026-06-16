import pytest

from utils.utils import _extract_json_ld_jobposting, parse_job_listing


def test_json_ld_jobposting_extraction_reads_core_fields():
    html = '''
    <html><head><script type="application/ld+json">
    {
      "@context": "https://schema.org",
      "@type": "JobPosting",
      "title": "Backend Engineer",
      "hiringOrganization": {"name": "Acme"},
      "description": "Build REST APIs using Python and SQL. Experience with Docker preferred."
    }
    </script></head><body></body></html>
    '''
    text = _extract_json_ld_jobposting(html)
    assert "Backend Engineer" in text
    assert "Acme" in text
    assert "Build REST APIs" in text


def test_parse_job_listing_rejects_empty_url():
    with pytest.raises(ValueError, match="valid job listing URL"):
        parse_job_listing("   ")
