import json
import os
import re
from html import escape
from typing import List

import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv

from prompts import cover_letter_prompts
from utils.utils import (
    analyze_resume_job_fit,
    assess_resume_extraction_quality,
    build_export_metadata,
    cover_letter_to_docx,
    cover_letter_to_pdf,
    generate_cover_letter,
    normalize_pasted_resume_text,
    parse_job_listing,
    parse_resume,
)

load_dotenv()
os.environ.setdefault(
    "USER_AGENT",
    "AI-Cover-Letter-Generator/1.0 (+https://github.com/aakanksha105/Cover-Letter-Generator)",
)

def extract_resume_contact_details(text: str) -> dict:
    """Best-effort extraction for export header fields. Keeps fields blank when uncertain."""
    text = text or ""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    email_match = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    phone_match = re.search(r"(?:\+?1[\s.-]?)?(?:\(?\d{3}\)?[\s.-]?)\d{3}[\s.-]?\d{4}", text)
    linkedin_match = re.search(r"(?:https?://)?(?:www\.)?linkedin\.com/in/[A-Za-z0-9_\-/%]+", text, re.I)
    github_match = re.search(r"(?:https?://)?(?:www\.)?github\.com/[A-Za-z0-9_\-/%]+", text, re.I)

    name = ""
    for line in lines[:8]:
        low = line.lower()
        if any(token in low for token in ["@", "linkedin", "github", "portfolio", "resume", "curriculum", "phone"]):
            continue
        words = re.findall(r"[A-Za-z]+", line)
        if 2 <= len(words) <= 4 and len(line) <= 60:
            name = line
            break

    return {
        "name": name,
        "email": email_match.group(0) if email_match else "",
        "phone": phone_match.group(0) if phone_match else "",
        "linkedin": linkedin_match.group(0) if linkedin_match else "",
        "portfolio": github_match.group(0) if github_match else "",
    }


def autofill_export_header_from_resume(resume_text: str):
    details = extract_resume_contact_details(resume_text)
    if details.get("name") and not st.session_state.export_candidate_name:
        st.session_state.export_candidate_name = details["name"]
    if details.get("email") and not st.session_state.export_email:
        st.session_state.export_email = details["email"]
    if details.get("phone") and not st.session_state.export_phone:
        st.session_state.export_phone = details["phone"]
    if details.get("linkedin") and not st.session_state.export_linkedin:
        st.session_state.export_linkedin = details["linkedin"]
    if details.get("portfolio") and not st.session_state.export_portfolio:
        st.session_state.export_portfolio = details["portfolio"]



def recommended_emphasis(fit: dict) -> list:
    matched = fit.get("matched_skills", []) if fit else []
    requirements = fit.get("requirement_lines", []) if fit else []
    emphasis = []
    for skill in matched[:4]:
        emphasis.append(str(skill))
    for line in requirements[:2]:
        clean = str(line).strip(" -•")
        if clean and len(clean) < 120:
            emphasis.append(clean)
    return emphasis[:5]


st.set_page_config(page_title="AI Cover Letter Generator", page_icon="✍️", layout="wide")

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
:root {
  --bg: #faf7f2;
  --card: #ffffff;
  --ink: #171926;
  --muted: #626a7a;
  --line: #e4d8cb;
  --line-strong: #cdbfac;
  --accent: #ee5548;
  --accent-dark: #d64538;
  --soft: #fff1ea;
  --violet-soft: #f2eaff;
  --violet: #6147d6;
  --green-bg: #ecfbf3;
  --green: #08733f;
  --orange-bg: #fff5eb;
  --orange: #9c4a14;
}
html, body, [class*="css"] {font-family: 'Inter', sans-serif;}
.stApp {background: var(--bg); color: var(--ink);}
.block-container {max-width: 1040px; padding-top: 5.7rem; padding-bottom: 3rem;}
section[data-testid="stSidebar"], #MainMenu, footer, div[data-testid="stToolbar"], header[data-testid="stHeader"], div[data-testid="stDecoration"] {display:none !important; visibility:hidden !important;}

.app-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 99999;
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:22px;
  padding: 10px max(24px, calc((100vw - 1040px) / 2)) 12px;
  background: var(--bg);
  border-bottom: 1px solid rgba(228, 216, 203, 0.9);
  box-shadow: 0 10px 24px rgba(35,25,8,.05);
}
.brand-link {text-decoration:none !important; color:inherit !important;}
.brand {display:flex; align-items:center; gap:12px;}
.brand-icon {
  width:42px; height:42px; border-radius:13px;
  display:flex; align-items:center; justify-content:center;
  background:linear-gradient(135deg, #fff0db, #ffe0d8);
  border:1px solid #e6d1bd; font-size:20px;
}
.brand-name {font-weight:850; font-size:25px; letter-spacing:-.45px; color:var(--ink); white-space:nowrap;}
.header-nav {display:flex; gap:12px; align-items:center; justify-content:flex-end;}
.nav-link {
  display:inline-flex; align-items:center; justify-content:center;
  min-height:42px; padding:0 22px;
  border-radius:14px; border:1px solid var(--line-strong);
  background:#fff; color:var(--ink) !important; text-decoration:none !important;
  font-size:15px; font-weight:750; white-space:nowrap;
}
.nav-link:hover {border-color:var(--accent); color:var(--accent) !important;}
.nav-link.active {background:var(--accent); border-color:var(--accent); color:#fff !important;}
.nav-link.create {min-width:160px;}

.stButton > button, .stDownloadButton > button {
  white-space: nowrap !important;
  border-radius: 12px !important;
  border: 1px solid var(--line-strong) !important;
  min-height: 42px !important;
  font-weight: 700 !important;
  background: #ffffff !important;
  color: var(--ink) !important;
  box-shadow: none !important;
}
.stButton > button:hover, .stDownloadButton > button:hover {border-color: var(--accent) !important; color: var(--accent) !important;}

.export-actions [data-testid="column"] {
  display: flex;
  align-items: stretch;
}
.export-actions .stDownloadButton,
.export-actions .stDownloadButton > button {
  width: 100% !important;
}
.action-label {
  font-size: 14px;
  font-weight: 800;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: .08em;
  margin: 6px 0 12px;
}
.stButton > button[kind="primary"], .stDownloadButton > button[kind="primary"] {background: var(--accent) !important; color:#fff !important; border-color:var(--accent) !important;}
div[data-baseweb="input"] input, div[data-baseweb="textarea"] textarea, .stTextInput input, .stTextArea textarea {
  background: #ffffff !important;
  color: var(--ink) !important;
  border: 1px solid var(--line-strong) !important;
  border-radius: 12px !important;
  font-size: 15px !important;
}
.stTextInput label, .stTextArea label, .stFileUploader label, .stRadio label {
  color: var(--ink) !important; font-weight: 700 !important; font-size: 15px !important;
}
div[data-testid="stFileUploader"] section {
  background: #ffffff !important;
  border: 1.3px dashed #cdbfae !important;
  border-radius: 14px !important;
  min-height: 82px !important;
}
div[data-testid="stFileUploader"] section * {color: var(--ink) !important;}

.hero {
  background: linear-gradient(135deg, #ffffff 0%, #fffaf3 62%, #fff2ed 100%);
  border:1px solid var(--line);
  border-radius:24px;
  padding:34px;
  box-shadow:0 18px 48px rgba(35,25,8,.055);
}
.hero-grid {display:grid; grid-template-columns: 1fr .9fr; gap:34px; align-items:center;}
.eyebrow {display:inline-flex; padding:7px 13px; border-radius:999px; background:var(--violet-soft); color:var(--violet); font-weight:800; font-size:13.5px; margin-bottom:18px;}
.hero-title {font-size:40px; line-height:1.13; letter-spacing:-1.05px; margin:0 0 15px; color:var(--ink); font-weight:850;}
.hero-subtitle {font-size:16px; line-height:1.65; color:var(--muted); margin:0; max-width:520px;}
.home-note {font-size:13.5px; color:var(--muted); text-align:center; margin-top:8px;}
.info-panel {background:#fff; border:1px solid var(--line); border-radius:22px; padding:25px; box-shadow:0 14px 34px rgba(35,25,8,.045);}
.info-panel h3 {margin:0 0 14px; font-size:21px; color:var(--ink); letter-spacing:-.3px;}
.info-row {display:flex; gap:13px; align-items:flex-start; padding:12px 0; border-bottom:1px solid #f0e8de;}
.info-row:last-child {border-bottom:0; padding-bottom:0;}
.info-icon {width:36px; height:36px; border-radius:12px; background:var(--soft); display:flex; align-items:center; justify-content:center; flex-shrink:0;}
.info-text b {display:block; font-size:15px; color:var(--ink); margin-bottom:3px;}
.info-text span {font-size:14px; color:var(--muted); line-height:1.45;}
.feature-grid {display:grid; grid-template-columns:repeat(3,1fr); gap:15px; margin-top:20px;}
.feature-card {background:#fff; border:1px solid var(--line); border-radius:18px; padding:20px; box-shadow:0 8px 24px rgba(35,25,8,.03);}
.feature-card h3 {font-size:16px; margin:0 0 8px; color:var(--ink);}
.feature-card p {font-size:14px; line-height:1.55; color:var(--muted); margin:0;}

.page-heading {margin:4px 0 18px;}
.page-heading h1 {font-size:32px; line-height:1.15; letter-spacing:-.7px; margin:0 0 8px; color:var(--ink);}
.page-heading p {font-size:16px; color:var(--muted); margin:0; max-width:760px;}
.form-section {margin: 14px 0 12px; padding-top: 0;}
.section-title {font-size:24px; font-weight:850; margin:0 0 6px; color:var(--ink); letter-spacing:-.3px;}
.section-help {font-size:15px; color:var(--muted); margin:0 0 10px;}
.section-divider {height:1px; background:var(--line); margin:14px 0;}
.small-note {font-size:13.5px; color:var(--muted); margin-top:5px;}
.match-box {background:#fff; border:1px solid var(--line); border-radius:18px; padding:20px; margin-top:14px; box-shadow:0 8px 24px rgba(35,25,8,.03);}
.score {font-size:31px; font-weight:850; line-height:1; color:var(--ink);}
.chip {display:inline-block; margin:5px 6px 5px 0; padding:7px 10px; border-radius:999px; font-size:13px; font-weight:750; border:1px solid #d8d7d2; background:#fafafa; color:#303342;}
.chip.good {background:var(--green-bg); border-color:#bfe8d1; color:var(--green);}
.chip.miss {background:var(--orange-bg); border-color:#ffd5b4; color:var(--orange);}
.faq-card {background:#fff; border:1px solid var(--line); border-radius:16px; padding:18px 20px; margin-top:13px; box-shadow:0 8px 22px rgba(35,25,8,.025);}
.faq-card b {display:block; margin-bottom:7px; color:var(--ink); font-size:15.8px;}
.faq-card span {color:var(--muted); font-size:14.5px; line-height:1.6;}
@media (max-width: 900px) {
  .block-container {padding-top: 7.8rem;}
  .app-header {display:block; padding: 10px 18px 12px;}
  .header-nav {justify-content:flex-start; margin-top:12px; overflow-x:auto; padding-bottom:4px;}
  .hero-grid, .feature-grid {grid-template-columns:1fr;}
  .hero {padding:26px 21px;}
  .hero-title {font-size:31px;}
  .brand-name {font-size:21px;}
}
.hero-app-name {
  font-size: 1.15rem;
  font-weight: 850;
  color: var(--ink);
  margin-bottom: 0.8rem;
  letter-spacing: -0.02em;
}

.anchor-link {
  display: none !important;
  visibility: hidden !important;
}
</style>
"""


def init_state():
    defaults = {
        "page": "home",
        "resume_text": "",
        "job_url": "",
        "job_listing_text": "",
        "cover_letter": "",
        "fit_summary": None,
        "last_uploaded_name": "",
        "resume_quality": None,
        "manual_resume_text": "",
        "scroll_to_job_listing": False,
        "scroll_to_top": False,
        "pending_scroll_anchor": "",
        "pending_clear_job": False,
        "pending_start_over": False,
        "job_url_input": "",
        "export_candidate_name": "",
        "export_email": "",
        "export_phone": "",
        "export_linkedin": "",
        "export_portfolio": "",
        "export_company": "",
        "export_job_title": "",
        "include_export_header": True,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    query_page = st.query_params.get("page")
    if query_page in {"home", "create", "faq"}:
        st.session_state.page = query_page


def go(page: str):
    st.session_state.page = page
    st.query_params["page"] = page
    st.rerun()


def scroll_to_anchor(anchor_id: str):
    components.html(
        f"""
        <script>
        const parentWindow = window.parent;
        const parentDoc = parentWindow.document;
        const target = parentDoc.getElementById("{anchor_id}");
        if (target) {{
          setTimeout(() => {{
            target.scrollIntoView({{behavior: "smooth", block: "start"}});
            parentWindow.scrollBy(0, -92);
          }}, 120);
        }}
        </script>
        """,
        height=0,
    )




def schedule_scroll(anchor_id: str):
    """Queue a scroll target for later in the same rerun, after the target has rendered."""
    st.session_state.pending_scroll_anchor = anchor_id


def consume_scroll(anchor_id: str):
    """Scroll only when the queued target is now visible on the page."""
    if st.session_state.get("pending_scroll_anchor") == anchor_id:
        st.session_state.pending_scroll_anchor = ""
        scroll_to_anchor(anchor_id)


def scroll_to_page_top():
    components.html(
        """
        <script>
        const parentWindow = window.parent;
        const parentDoc = parentWindow.document;
        const scrollTargets = [
          parentWindow,
          parentDoc.scrollingElement,
          parentDoc.documentElement,
          parentDoc.body,
          parentDoc.querySelector('[data-testid="stAppViewContainer"]'),
          parentDoc.querySelector('section.main')
        ].filter(Boolean);

        function goTop() {
          scrollTargets.forEach((el) => {
            try {
              if (el === parentWindow) {
                el.scrollTo({top: 0, left: 0, behavior: 'smooth'});
              } else {
                el.scrollTop = 0;
              }
            } catch (e) {}
          });
        }
        goTop();
        setTimeout(goTop, 100);
        setTimeout(goTop, 350);
        </script>
        """,
        height=0,
    )


def header():
    current = st.session_state.get("page", "home")

    def active(name: str) -> str:
        return " active" if current == name else ""

    st.markdown(
        f'''<div class="app-header">
              <a class="brand-link" href="?page=home" target="_self">
                <div class="brand">
                  <div class="brand-icon">✍️</div>
                  <div class="brand-name">Cover Letter AI</div>
                </div>
              </a>
              <div class="header-nav">
                <a class="nav-link{active('home')}" href="?page=home" target="_self">Home</a>
                <a class="nav-link create{active('create')}" href="?page=create" target="_self">Create Cover Letter</a>
                <a class="nav-link{active('faq')}" href="?page=faq" target="_self">FAQ</a>
              </div>
            </div>''',
        unsafe_allow_html=True,
    )


def chip_list(items: List[str], klass: str = ""):
    if not items:
        st.caption("None detected yet.")
        return
    html = "".join(f'<span class="chip {klass}">{escape(str(item))}</span>' for item in items[:18])
    st.markdown(html, unsafe_allow_html=True)



def home_page():
    header()
    st.markdown(
        """
        <div class="hero">
          <div class="hero-grid">
            <div>
              <div class="hero-app-name">Cover Letter AI</div>
              <div class="eyebrow">Role-matched drafts</div>
              <h1 class="hero-title">Create a tailored cover letter from your resume and job listing.</h1>
              <p class="hero-subtitle">Upload your resume, fetch or paste the job description, review matched keywords, and generate an editable cover letter.</p>
            </div>
            <div class="info-panel">
              <h3>What the app does</h3>
              <div class="info-row"><div class="info-icon">📄</div><div class="info-text"><b>Reads your resume</b><span>Supports PDF and DOCX files.</span></div></div>
              <div class="info-row"><div class="info-icon">🔗</div><div class="info-text"><b>Uses the job listing</b><span>Fetch a URL or paste the full description.</span></div></div>
              <div class="info-row"><div class="info-icon">🧠</div><div class="info-text"><b>Matches keywords</b><span>Compares job skills against resume skills.</span></div></div>
              <div class="info-row"><div class="info-icon">⬇️</div><div class="info-text"><b>Exports your letter</b><span>Download as TXT, DOCX, or PDF.</span></div></div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")
    if st.button("Start creating", type="primary", use_container_width=True):
        go("create")
    st.markdown('<div class="home-note">Upload resume · Add job listing · Generate and export</div>', unsafe_allow_html=True)


def faq_page():
    header()
    st.markdown('<div class="page-heading"><h1>FAQ</h1><p>Important questions about how the generator works.</p></div>', unsafe_allow_html=True)
    faqs = [
        ("How does the app create a cover letter?", "It parses your resume, reads the job listing, compares important job keywords with your resume, and sends both texts to the OpenAI/LangChain prompt to generate a tailored draft."),
        ("Why should I paste the full job description?", "Job boards can block or hide content from URL extraction. Pasting the full description gives the most accurate keyword match and cover letter."),
        ("What happens when I click Fetch job description?", "The app tries to read structured job posting data first, then uses browser-based extraction and fallback text extraction. You can edit the fetched text before generating."),
        ("Why does the keyword match matter?", "It shows which tools, technologies, and role keywords appear in both the job listing and your resume before the cover letter is generated."),
        ("Can I edit the generated cover letter?", "Yes. The draft appears in an editable text box before downloading."),
        ("Which file formats are supported?", "Resume upload supports PDF and DOCX. Cover letter export supports TXT, DOCX, and PDF."),
        ("Does the app permanently store my resume?", "No database storage is used in this version. Your resume and job listing stay in the current Streamlit session."),
        ("What should I do if the job link fetch is incomplete?", "Paste the full job description manually in the job description box. This is usually the most reliable option."),
    ]
    for q, a in faqs:
        st.markdown(f'<div class="faq-card"><b>{q}</b><span>{a}</span></div>', unsafe_allow_html=True)


def request_clear_job(scroll_to_job: bool = False):
    st.session_state.pending_clear_job = True
    st.session_state.scroll_to_job_listing = scroll_to_job
    st.rerun()


def request_start_over():
    st.session_state.pending_start_over = True
    st.query_params["page"] = "home"
    st.rerun()


def apply_pending_resets():
    if st.session_state.get("pending_start_over"):
        for key in [
            "resume_text",
            "job_url",
            "job_url_input",
            "job_listing_text",
            "cover_letter",
            "last_uploaded_name",
            "manual_resume_text",
            "export_candidate_name",
            "export_email",
            "export_phone",
            "export_linkedin",
            "export_portfolio",
            "export_company",
            "export_job_title",
        ]:
            st.session_state[key] = ""
        st.session_state.fit_summary = None
        st.session_state.resume_quality = None
        st.session_state.include_export_header = True
        st.session_state.scroll_to_job_listing = False
        st.session_state.scroll_to_top = False
        st.session_state.pending_scroll_anchor = ""
        st.session_state.pending_clear_job = False
        st.session_state.pending_start_over = False
        st.session_state.page = "home"
        st.query_params["page"] = "home"
        return

    if st.session_state.get("pending_clear_job"):
        st.session_state.job_url = ""
        st.session_state.job_url_input = ""
        st.session_state.job_listing_text = ""
        st.session_state.cover_letter = ""
        st.session_state.fit_summary = None
        st.session_state.pending_scroll_anchor = "job-listing-section" if st.session_state.get("scroll_to_job_listing") else ""
        st.session_state.pending_clear_job = False

def create_page():
    header()
    if st.session_state.get("scroll_to_top"):
        st.session_state.scroll_to_top = False
        scroll_to_page_top()
    st.markdown(
        '<div class="page-heading"><h1>Create your cover letter</h1><p>Complete each step below to generate an editable, job-specific cover letter.</p></div>',
        unsafe_allow_html=True,
    )
    st.progress(0.2 if not st.session_state.resume_text else 0.45 if not st.session_state.job_listing_text.strip() else 0.7 if not st.session_state.cover_letter else 1.0)
    if not os.getenv("OPENAI_API_KEY"):
        st.info("OpenAI API key is missing. You can still parse resume/job text, but generation needs OPENAI_API_KEY in .env.")

    st.markdown('<div class="form-section"><div class="section-title">Step 1 · Resume</div><p class="section-help">Upload a PDF/DOCX or paste resume text if extraction looks incomplete.</p></div>', unsafe_allow_html=True)
    resume_source = st.radio("Resume input method", ("Upload file", "Paste text"), horizontal=True)

    if resume_source == "Upload file":
        resume_file = st.file_uploader("Upload resume", type=["pdf", "docx"], label_visibility="collapsed")
        if resume_file is not None and resume_file.name != st.session_state.last_uploaded_name:
            try:
                with st.spinner("Reading resume..."):
                    st.session_state.resume_text = parse_resume(resume_file)
                    st.session_state.resume_quality = assess_resume_extraction_quality(st.session_state.resume_text)
                    autofill_export_header_from_resume(st.session_state.resume_text)
                st.session_state.last_uploaded_name = resume_file.name
                st.success("Resume parsed successfully.")
            except Exception as exc:
                st.error(f"Could not parse the resume: {exc}")
                st.info("Try the Paste text option to continue without relying on file extraction.")
    else:
        st.session_state.manual_resume_text = st.text_area(
            "Paste resume text",
            value=st.session_state.manual_resume_text,
            height=220,
            placeholder="Paste your resume text here...",
        )
        if st.button("Use pasted resume text", use_container_width=True):
            cleaned = normalize_pasted_resume_text(st.session_state.manual_resume_text)
            if len(cleaned.split()) < 80:
                st.warning("The pasted resume text looks very short. Paste the full resume for better results.")
            else:
                st.session_state.resume_text = cleaned
                st.session_state.resume_quality = assess_resume_extraction_quality(cleaned)
                autofill_export_header_from_resume(cleaned)
                st.session_state.last_uploaded_name = "manual-paste"
                st.success("Pasted resume text is ready.")

    if st.session_state.resume_text:
        st.markdown('<div id="resume-review-section"></div>', unsafe_allow_html=True)
        quality = st.session_state.resume_quality or assess_resume_extraction_quality(st.session_state.resume_text)
        if quality.get("warnings"):
            st.warning("Resume extraction may need review: " + " ".join(quality["warnings"]))
            st.caption("Use the Paste text option if the preview looks scrambled or incomplete.")
        else:
            pass
        with st.expander("Review extracted resume text"):
            st.text_area("Resume preview", st.session_state.resume_text, height=170, label_visibility="collapsed")

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    st.markdown('<div id="job-listing-section"></div>', unsafe_allow_html=True)
    st.markdown('<div class="form-section"><div class="section-title">Step 2 · Job listing</div><p class="section-help">Paste the full job description for the most accurate match.</p></div>', unsafe_allow_html=True)
    if st.session_state.get("scroll_to_job_listing"):
        st.session_state.scroll_to_job_listing = False
        scroll_to_anchor("job-listing-section")

    with st.form("job_fetch_form", clear_on_submit=False):
        st.text_input(
            "Job URL",
            key="job_url_input",
            placeholder="https://company.com/careers/job-posting",
        )
        c1, c2 = st.columns([2, 1])
        with c1:
            fetch_clicked = st.form_submit_button("Fetch job description", use_container_width=True)
        with c2:
            clear_clicked = st.form_submit_button("Clear job", use_container_width=True)

    if clear_clicked:
        request_clear_job(scroll_to_job=True)

    if fetch_clicked:
        job_url = st.session_state.job_url_input.strip()
        if not job_url:
            st.warning("Paste a job URL first.")
        else:
            try:
                with st.spinner("Fetching job description..."):
                    st.session_state.job_listing_text = parse_job_listing(job_url)
                st.session_state.job_url = job_url
                st.session_state.fit_summary = None
                st.session_state.cover_letter = ""
                st.success("Job description fetched. Review it below.")
            except Exception as exc:
                st.error("This job board may block automated extraction. Please paste the job description manually.")
                st.caption(str(exc))

    st.markdown('<div id="job-description-section"></div>', unsafe_allow_html=True)
    height = 150 if len(st.session_state.job_listing_text.strip()) < 100 else 280
    st.text_area(
        "Job description",
        key="job_listing_text",
        height=height,
        placeholder="Paste the full job description here...",
    )
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    st.markdown('<div class="form-section"><div class="section-title">Step 3 · Preview keyword match</div><p class="section-help">Review matched and missing skills from the job description.</p></div>', unsafe_allow_html=True)
    if st.button("Preview keyword match", use_container_width=True):
        if not st.session_state.resume_text or not st.session_state.job_listing_text.strip():
            st.warning("Upload a resume and add a job description first.")
        else:
            with st.spinner("Analyzing keywords..."):
                st.session_state.fit_summary = analyze_resume_job_fit(st.session_state.resume_text, st.session_state.job_listing_text)

    if st.session_state.fit_summary:
        st.markdown('<div id="keyword-results-section"></div>', unsafe_allow_html=True)
        fit = st.session_state.fit_summary
        a, b, c = st.columns([0.65, 1.6, 1.6])
        with a:
            st.markdown(f'<div class="score">{fit["fit_score"]}%</div>', unsafe_allow_html=True)
            st.caption("keyword fit")
        with b:
            st.markdown("**Matched keywords**")
            chip_list(fit.get("matched_skills", []), "good")
        with c:
            st.markdown("**Missing from resume**")
            chip_list(fit.get("missing_skills", []), "miss")
        requirement_lines = fit.get("requirement_lines", [])
        if requirement_lines:
            st.markdown("**Important requirement lines**")
            for line in requirement_lines[:6]:
                st.write(f"- {line}")
        emphasis = recommended_emphasis(fit)
        if emphasis:
            st.markdown("**Recommended emphasis**")
            st.write("Focus the draft on: " + ", ".join(emphasis))

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    st.markdown('<div class="form-section"><div class="section-title">Step 4 · Generate</div><p class="section-help">Choose a style and length, then create your cover letter.</p></div>', unsafe_allow_html=True)
    g1, g2 = st.columns(2)
    with g1:
        style = st.radio(
            "Style",
            ["Professional", "Modern"],
            horizontal=True,
            index=0,
        )
    with g2:
        length = st.radio(
            "Length",
            ["Short", "Medium", "Detailed"],
            horizontal=True,
            index=1,
        )

    if st.button("Generate tailored cover letter", type="primary", use_container_width=True):
        if not os.getenv("OPENAI_API_KEY"):
            st.error("OPENAI_API_KEY is missing. Add it to your .env file.")
        elif not st.session_state.resume_text or not st.session_state.job_listing_text.strip():
            st.warning("Upload a resume and add a job description first.")
        else:
            template = (
                getattr(cover_letter_prompts, "prompt_template", None)
                if style == "Professional"
                else getattr(cover_letter_prompts, "modern_template", None)
            )
            if template is None:
                template = (
                    cover_letter_prompts.prompt_template_classic
                    if style == "Professional"
                    else cover_letter_prompts.prompt_template_modern
                )
            try:
                with st.spinner("Analyzing keyword match..."):
                    st.session_state.fit_summary = analyze_resume_job_fit(
                        st.session_state.resume_text,
                        st.session_state.job_listing_text,
                    )
                    with st.spinner("Drafting tailored cover letter..."):
                        st.session_state.cover_letter = generate_cover_letter(
                            st.session_state.resume_text,
                            st.session_state.job_listing_text,
                            template,
                            st.session_state.fit_summary,
                            length=length,
                        )
                    schedule_scroll("draft-section")
            except Exception as exc:
                st.error(f"Could not generate the cover letter: {exc}")

    if st.session_state.cover_letter:
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        st.markdown('<div id="draft-section"></div>', unsafe_allow_html=True)
        consume_scroll("draft-section")
        st.markdown('<div class="form-section"><div class="section-title">Step 5 · Edit and download</div><p class="section-help">Make final edits and download your cover letter.</p></div>', unsafe_allow_html=True)
        st.session_state.cover_letter = st.text_area(
            "Generated cover letter",
            value=st.session_state.cover_letter,
            height=360,
            label_visibility="collapsed",
        )

        with st.expander("Optional contact header for DOCX/PDF", expanded=False):
            st.session_state.include_export_header = st.checkbox(
                "Add name and contact details to DOCX/PDF",
                value=st.session_state.include_export_header,
            )
            h1, h2 = st.columns(2)
            with h1:
                st.session_state.export_candidate_name = st.text_input(
                    "Your name", value=st.session_state.export_candidate_name, placeholder="Jane Doe"
                )
                st.session_state.export_email = st.text_input(
                    "Email", value=st.session_state.export_email, placeholder="jane@email.com"
                )
                st.session_state.export_phone = st.text_input(
                    "Phone", value=st.session_state.export_phone, placeholder="+1 555 555 5555"
                )
            with h2:
                st.session_state.export_linkedin = st.text_input(
                    "LinkedIn", value=st.session_state.export_linkedin, placeholder="linkedin.com/in/janedoe"
                )
                st.session_state.export_portfolio = st.text_input(
                    "Portfolio/GitHub", value=st.session_state.export_portfolio, placeholder="github.com/janedoe"
                )
                st.session_state.export_company = st.text_input(
                    "Company", value=st.session_state.export_company, placeholder="Company name"
                )
                st.session_state.export_job_title = st.text_input(
                    "Job title", value=st.session_state.export_job_title, placeholder="Software Engineer"
                )
            st.caption("Use name, email, phone, LinkedIn, and portfolio/GitHub. A street address is not needed for most online applications.")

        export_metadata = build_export_metadata(
            candidate_name=st.session_state.export_candidate_name,
            email=st.session_state.export_email,
            phone=st.session_state.export_phone,
            linkedin=st.session_state.export_linkedin,
            portfolio=st.session_state.export_portfolio,
            company=st.session_state.export_company,
            job_title=st.session_state.export_job_title,
            include_header=st.session_state.include_export_header,
        )

        st.markdown('<div class="export-actions">', unsafe_allow_html=True)
        d1, d2, d3 = st.columns(3)
        with d1:
            st.download_button(
                "Download TXT",
                data=st.session_state.cover_letter,
                file_name="cover_letter.txt",
                mime="text/plain",
                use_container_width=True,
            )
        with d2:
            st.download_button(
                "Download DOCX",
                data=cover_letter_to_docx(st.session_state.cover_letter, metadata=export_metadata),
                file_name="cover_letter.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
            )
        with d3:
            st.download_button(
                "Download PDF",
                data=cover_letter_to_pdf(st.session_state.cover_letter, metadata=export_metadata),
                file_name="cover_letter.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    b1, b2 = st.columns(2)
    with b1:
        if st.button("Use another job listing", use_container_width=True):
            request_clear_job(scroll_to_job=True)
    with b2:
        if st.button("Start over", use_container_width=True):
            request_start_over()


def main():
    init_state()
    apply_pending_resets()
    st.markdown(CSS, unsafe_allow_html=True)
    page = st.session_state.get("page", "home")
    if page == "create":
        create_page()
    elif page == "faq":
        faq_page()
    else:
        home_page()


if __name__ == "__main__":
    main()
