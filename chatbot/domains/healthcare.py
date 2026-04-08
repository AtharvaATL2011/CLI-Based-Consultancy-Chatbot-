from chatbot.config import PROMPTS_DIR

_FALLBACK_PROMPT = """You are a compassionate health information assistant.
NEVER diagnose or prescribe. Always advise consulting a doctor.
For emergencies, immediately direct to emergency services.
Be empathetic — people asking health questions may be worried."""

_EMERGENCY_KEYWORDS = [
    "chest pain", "can't breathe", "cannot breathe", "difficulty breathing",
    "heart attack", "stroke", "unconscious", "not breathing", "severe bleeding",
    "overdose", "suicidal", "suicide", "kill myself",
]

_EMERGENCY_RESPONSE = (
    "\n\n🚨 **If this is a medical emergency, call emergency services "
    "(112 or your local number) immediately.**"
)


def get_system_prompt() -> str:
    prompt_file = PROMPTS_DIR / "healthcare.txt"
    if prompt_file.exists():
        return prompt_file.read_text(encoding="utf-8").strip()
    return _FALLBACK_PROMPT


def enrich_message(user_message: str) -> str:
    return user_message


def is_emergency(message: str) -> bool:
    lower = message.lower()
    return any(kw in lower for kw in _EMERGENCY_KEYWORDS)


def add_disclaimer(response: str) -> str:
    return response + (
        "\n\n---\n*⚕️ General information only — not medical advice. "
        "Consult a qualified healthcare professional for personal guidance.*"
    )