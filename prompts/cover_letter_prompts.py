try:
    from langchain_core.prompts import PromptTemplate
except Exception:  # pragma: no cover - lightweight fallback for local tests/docs
    class _SimplePromptTemplate:
        def __init__(self, template: str, partials=None):
            self.template = template
            self.partials = partials or {}

        @classmethod
        def from_template(cls, template: str):
            return cls(template)

        def partial(self, **kwargs):
            merged = dict(self.partials)
            merged.update(kwargs)
            return _SimplePromptTemplate(self.template, merged)

        def format(self, **kwargs):
            merged = dict(self.partials)
            merged.update(kwargs)
            return self.template.format(**merged)

    PromptTemplate = _SimplePromptTemplate
COMMON_RULES = """
Important rules:
- Do not invent experience, tools, metrics, companies, degrees, certifications, or projects.
- Only use skills and experience that are supported by the resume text.
- If the job asks for something that is not clearly present in the resume, avoid claiming direct experience with it.
- Keep the writing professional, concise, and specific to the job listing.
- Use the keyword fit summary to prioritize resume-backed matches and important job requirements.
- Do not claim missing skills listed in the fit summary unless the resume clearly supports them.
- Follow the requested length guidance exactly; the selected length should visibly change the amount of detail.
- Avoid generic filler such as "I am writing to express my interest" when a stronger opening is possible.
"""

prompt_template_classic = PromptTemplate.from_template(
    """Given the following resume and job listing, generate a tailored cover letter for a job application.

{rules}

Format requirements:
- Do not include sender or recipient contact information.
- Use this cover-letter structure: salutation, opening paragraph naming the role/company, 2-3 body paragraphs with resume-backed examples, closing paragraph, sign-off with candidate name.
- Include a simple salutation such as "Dear Hiring Manager," unless a hiring manager name is clearly present.
- Keep paragraphs separated by blank lines.
- Put the candidate name on the line immediately after the sign-off, for example: Sincerely, then a new line with the candidate name.
- Follow the selected length guidance for word count and paragraph count.
- Use business casual language.
- Highlight overlap between the resume and job listing, especially technologies, responsibilities, and domain experience.
- End with a confident call to action.

------------
Resume:
{resume}
------------
Job Listing:
{job_listing}
------------
Keyword Fit Summary:
{fit_summary}
------------
Generation Options:
{generation_options}
------------
Cover Letter:"""
).partial(rules=COMMON_RULES)

prompt_template_modern = PromptTemplate.from_template(
    """Given the following resume and job listing, generate a concise answer to the application prompt: "Tell us about yourself?"

{rules}

Format requirements:
- Begin with: "Hi, I'm <candidate name>, <short role-focused tagline>."
- Follow the selected length guidance for word count and paragraph count.
- Use business casual language.
- Highlight relevant overlap between the resume and job listing.
- End with a confident, forward-looking sentence.

------------
Resume:
{resume}
------------
Job Listing:
{job_listing}
------------
Keyword Fit Summary:
{fit_summary}
------------
Generation Options:
{generation_options}
------------
Answer:"""
).partial(rules=COMMON_RULES)

# Backward-compatible names used by app.py and the original project flow.
prompt_template = prompt_template_classic
modern_template = prompt_template_modern
