import os

from dotenv import load_dotenv
from langchain_openrouter import ChatOpenRouter


load_dotenv()


def get_llm():
    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        raise ValueError(
            "OPENROUTER_API_KEY is not set. "
            "Add it to the .env file."
        )

    return ChatOpenRouter(
        model="openai/gpt-4.1-mini",
        temperature=0,
        max_tokens=1000,
    )