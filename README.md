# AI Cover Letter Generator

A Streamlit application that creates editable, job-specific cover letters from a resume and job description. The app parses PDF/DOCX resumes, accepts job URLs or pasted job descriptions, previews keyword match, and exports the final cover letter as TXT, DOCX, or PDF.

> Live demo: add your deployed Streamlit Cloud or Render URL here.

## What it does

- Reads a PDF/DOCX resume or accepts pasted resume text.
- Warns when resume extraction looks short or unreliable.
- Fetches job descriptions from URLs when possible.
- Supports manual job-description paste when job boards block extraction.
- Shows matched skills, missing skills, important requirement lines, and recommended emphasis.
- Sends the resume, job description, and keyword-fit summary into the cover-letter prompt.
- Generates a cover letter in two styles: **Professional** or **Modern**.
- Supports three lengths: **Short**, **Medium**, and **Detailed**.
- Lets users edit the generated letter before exporting.
- Exports TXT, DOCX, and PDF.
- Optionally adds a clean contact header to DOCX/PDF exports.

## Tech stack

| Area | Tools |
|---|---|
| UI | Streamlit, custom CSS |
| LLM | OpenAI API, LangChain |
| Resume parsing | pypdf, python-docx |
| Job extraction | Playwright, requests, BeautifulSoup, trafilatura, JSON-LD parsing |
| Keyword analysis | Python, regex, curated skill catalog, optional LLM skill extraction |
| Export | python-docx, ReportLab |
| Testing | pytest |
| Packaging | Poetry, Docker |

## Architecture

```mermaid
flowchart LR
    A[Resume Upload or Paste] --> B[Parse Resume + Quality Check]
    C[Job URL or Paste JD] --> D[Extract/Clean Job Description]
    B --> E[Keyword Fit Analysis]
    D --> E
    E --> F[Prompt with Fit Summary]
    B --> F
    D --> F
    F --> G[Generate Cover Letter]
    G --> H[Edit + Export TXT/DOCX/PDF]
```

## Project structure

```text
Cover-Letter-Generator/
├── app.py
├── agents/
│   ├── __init__.py
│   └── openai_client.py
├── prompts/
│   ├── __init__.py
│   ├── cover_letter_prompts.py
│   └── job_listing_prompt.py
├── utils/
│   ├── __init__.py
│   └── utils.py
├── tests/
│   ├── conftest.py
│   ├── test_app_helpers.py
│   ├── test_exports_and_prompts.py
│   ├── test_fit_analysis.py
│   └── test_resume_parsing.py
├── assets/
├── .env.example
├── requirements.txt
├── pyproject.toml
├── poetry.lock
├── Dockerfile
├── docker-compose.yml
├── DEPLOYMENT.md
└── README.md
```

## Environment setup

Copy the example environment file:

```bash
cp .env.example .env
```

Then add your OpenAI API key:

```env
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4o-mini
USER_AGENT=AI-Cover-Letter-Generator/1.0
```

Do **not** commit your real `.env` file.

## Run locally with Poetry

```bash
poetry install
poetry run playwright install chromium
poetry run streamlit run app.py
```

Then open:

```text
http://localhost:8501
```

## Run locally with pip

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python -m playwright install chromium
streamlit run app.py
```

## Run tests

```bash
poetry run pytest
```

or:

```bash
pytest
```

Current test coverage includes 21 automated tests across these areas:

- DOCX paragraph and table parsing
- Pasted resume normalization
- Resume extraction quality warnings
- Keyword matching and false-positive avoidance
- Requirement-line extraction
- Prompt formatting with fit summary and generation options
- Contact-detail extraction for export headers
- DOCX/PDF export generation
- DOCX/PDF professional header formatting
- Closing/signature formatting

## Docker

Docker is optional. The app can run locally with Poetry or pip without Docker.

Use Docker if you want a reproducible environment with Playwright/Chromium included:

```bash
docker build -t cover-letter-generator .
docker run --env-file .env -p 8501:8501 cover-letter-generator
```

Or with Docker Compose:

```bash
docker compose up --build
```

Then open:

```text
http://localhost:8501
```

## Deployment

`DEPLOYMENT.md` is not strictly required for GitHub, but it is useful if you want the repository to look deployment-ready. It contains Streamlit Cloud, Render, and Hugging Face Spaces notes.

For the simplest deployment, use Streamlit Cloud:

1. Push this project to GitHub.
2. Create a Streamlit Cloud app.
3. Select `app.py` as the entry file.
4. Add these secrets/environment variables:

```toml
OPENAI_API_KEY="your_key_here"
OPENAI_MODEL="gpt-4o-mini"
USER_AGENT="AI-Cover-Letter-Generator/1.0"
```

## How to use

1. Upload a resume or paste resume text.
2. Review the extracted resume text if needed.
3. Paste a job description or fetch it from a URL.
4. Preview keyword match.
5. Choose style and length.
6. Generate the cover letter.
7. Edit the result.
8. Download TXT, DOCX, or PDF.

## Cover letter export format

For DOCX/PDF exports, the optional contact header uses a modern online-application format:

```text
Candidate Name
Email | Phone | LinkedIn | Portfolio/GitHub

Date
Company — Job Title

Dear Hiring Manager,
...

Sincerely,
Candidate Name
```

A street address is intentionally not included because most modern online tech applications do not require one.

## Known limitations

- Some job boards block automated URL extraction. Paste the job description manually if fetch results are incomplete.
- Scanned/image-only PDFs may not parse correctly without OCR.
- Multi-column or highly designed resumes may require manual paste review.
- Generated letters should always be reviewed before submission.
- The app does not submit job applications automatically.

## Future improvements

- OCR support for scanned resumes.
- Structured JSON parsing for resume and job fields before generation.
- Streaming generation output.
- Optional saved history with user-controlled storage.
- End-to-end UI tests with Playwright.

## Resume / portfolio summary

**AI Cover Letter Generator** — Built a Streamlit app using Python, OpenAI/LangChain, PDF/DOCX parsing, job-description extraction, keyword-fit analysis, and DOCX/PDF export to generate editable, resume-aware cover letters.
