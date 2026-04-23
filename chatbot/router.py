"""
router.py — detects which domain a user message belongs to.
"""

from chatbot.llm import quick_classify
from chatbot.config import VALID_DOMAINS, DEFAULT_DOMAIN

_CLASSIFICATION_PROMPT = """Classify the user message into exactly one of these domains:
- education    (learning, studying, explaining concepts, homework, science, math, history)
- healthcare   (symptoms, medicine, mental health, fitness, nutrition, doctors)
- finance      (money, budgeting, savings, investing, taxes, debt, salary)
- programming  (coding, programming, software, bugs, algorithms, web dev, databases, APIs, code review)
- general      (anything else, greetings, unclear, out-of-scope)

User message: "{message}"

Respond with ONE word only from the list above."""


def classify(message: str) -> str:
    prompt = _CLASSIFICATION_PROMPT.format(message=message.strip())
    try:
        result = quick_classify(prompt).strip().lower()
        if result in VALID_DOMAINS:
            return result
        return DEFAULT_DOMAIN
    except Exception:
        return DEFAULT_DOMAIN


def domain_label(domain: str) -> str:
    labels = {
        "education":   "📚 Education",
        "healthcare":  "🏥 Healthcare",
        "finance":     "💰 Finance",
        "programming": "💻 Programming",
        "general":     "💬 General",
    }
    return labels.get(domain, "💬 General")