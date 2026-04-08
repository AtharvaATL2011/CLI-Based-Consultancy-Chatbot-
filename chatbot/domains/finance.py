from chatbot.config import PROMPTS_DIR

_FALLBACK_PROMPT = """You are a friendly financial literacy guide.
NOT a licensed advisor. For major decisions, recommend consulting a CA or CFP.
Be non-judgmental. Focus on education and empowerment.
Use simple language and explain all financial terms."""


def get_system_prompt() -> str:
    prompt_file = PROMPTS_DIR / "finance.txt"
    if prompt_file.exists():
        return prompt_file.read_text(encoding="utf-8").strip()
    return _FALLBACK_PROMPT


def enrich_message(user_message: str) -> str:
    return user_message


def add_disclaimer(response: str) -> str:
    return response + (
        "\n\n---\n*💼 General financial information only. "
        "Consult a certified financial advisor for significant decisions.*"
    )