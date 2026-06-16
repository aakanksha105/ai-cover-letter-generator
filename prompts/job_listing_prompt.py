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

prompt_template = PromptTemplate.from_template(
    """Extract the useful job listing content from the raw webpage text.

Keep only information needed to tailor a cover letter and identify job keywords.

Include:
- Role title if clearly present
- Company or product overview if clearly present
- Responsibilities
- Required qualifications
- Preferred qualifications
- Tools, technologies, platforms, frameworks, data/BI/ML keywords

Remove:
- cookie banners
- navigation/menu text
- apply button text
- benefits-only sections
- legal disclaimers
- equal opportunity statements
- unrelated page content

Do not invent missing fields. If the raw text is messy, preserve the clearest job requirements and skills.

Raw webpage text:
{raw_text}

Clean job description:"""
)
