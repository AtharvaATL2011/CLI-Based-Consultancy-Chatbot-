from pathlib import Path
from chatbot.config import PROMPTS_DIR

_FALLBACK_PROMPT = """You are a knowledgeable, patient, and encouraging tutor.
Help users understand concepts clearly at their level.
Use simple language, analogies, and real-world examples.
Break complex topics into small steps. Offer to quiz after explaining."""


def get_system_prompt() -> str:
    prompt_file = PROMPTS_DIR / "education.txt"
    if prompt_file.exists():
        return prompt_file.read_text(encoding="utf-8").strip()
    return _FALLBACK_PROMPT


def enrich_message(user_message: str) -> str:
    return user_message