# Deployment Guide

This file is optional for GitHub, but useful if you want the project to look deployment-ready.

## Streamlit Cloud

Recommended for this project because the app is already built with Streamlit.

1. Push the project to GitHub.
2. Create a new app on Streamlit Cloud.
3. Select the repository and set the entry file to `app.py`.
4. Add secrets/environment variables:

```toml
OPENAI_API_KEY="your_key_here"
OPENAI_MODEL="gpt-4o-mini"
USER_AGENT="AI-Cover-Letter-Generator/1.0"
```

5. Deploy and add the live URL to the README, GitHub repo description, portfolio, and resume.

## Render

Use Render if you want to deploy with Docker.

1. Push this project to GitHub.
2. Create a new Web Service.
3. Choose Docker as the environment.
4. Add environment variables from `.env.example`.
5. Expose port `8501`.

## Hugging Face Spaces

1. Create a new Streamlit Space.
2. Connect GitHub or upload the project.
3. Add secrets/environment variables.
4. Use `app.py` as the app entry file.

## Notes

- Never upload a real `.env` file.
- Some job boards block automated extraction; paste the job description manually if needed.
- URL extraction uses Playwright/Chromium, so the deployment environment must support Chromium installation.
