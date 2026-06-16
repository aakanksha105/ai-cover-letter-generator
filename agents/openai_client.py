import os
from langchain_openai import ChatOpenAI


def get_agent(temperature: float = 0.0):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")

    return ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        temperature=temperature,
        api_key=api_key,
    )
