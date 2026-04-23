"""
llm.py — GitHub Models API wrapper (OpenAI-compatible).
GPT-4.1 for general use, o4-mini for focused review tasks.
"""

import os
import time
from openai import OpenAI, RateLimitError
from chatbot.config import ANTHROPIC_API_KEY, MODEL, TEMPERATURE, MAX_TOKENS

_client = OpenAI(
    api_key=ANTHROPIC_API_KEY,
    base_url=os.getenv("OPENAI_BASE_URL", "https://models.github.ai/inference"),
)


def chat(
    messages: list[dict],
    system_prompt: str = "",
    model: str = MODEL,
    max_tokens: int = MAX_TOKENS,
    temperature: float = TEMPERATURE,
    retries: int = 3,
    retry_delay: int = 5,
) -> str:
    full_messages = []
    if system_prompt:
        full_messages.append({"role": "system", "content": system_prompt})
    full_messages.extend(messages)

    # Trim based on which model is being used
    # o4-mini free tier: 4000 token limit (~8000 chars)
    # gpt-4.1 free tier: 1M token limit (~800000 chars)
    if "o4-mini" in model or "o3-mini" in model:
        full_messages = _trim_messages(full_messages, max_input_chars=8000)
    else:
        full_messages = _trim_messages(full_messages, max_input_chars=28000)

    for attempt in range(retries):
        try:
            response = _client.chat.completions.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=full_messages,
            )
            return response.choices[0].message.content

        except RateLimitError:
            if attempt < retries - 1:
                wait = retry_delay * (attempt + 1)
                print(f"\n[Rate limited] Waiting {wait}s before retry ({attempt + 1}/{retries - 1})...")
                time.sleep(wait)
            else:
                return (
                    "The AI service is temporarily rate-limited. "
                    "Please wait 30 seconds and try again."
                )

        except Exception as e:
            return f"I ran into an issue: {e}\nPlease check your API key and try again."


def quick_classify(prompt: str) -> str:
    """Lightweight call for intent routing — always uses gpt-4.1."""
    full_messages = [
        {"role": "system", "content": "You are a classifier. Respond with exactly one word, nothing else."},
        {"role": "user", "content": prompt},
    ]
    try:
        response = _client.chat.completions.create(
            model=MODEL,  # always gpt-4.1 for routing — never reasoning model
            max_tokens=10,
            temperature=0.0,
            messages=full_messages,
        )
        return response.choices[0].message.content
    except Exception:
        return "general"


def _trim_messages(messages: list[dict], max_input_chars: int = 28000) -> list[dict]:
    """
    Trim oldest messages to stay within model input limits.
    Always keeps the latest user message intact.
    """
    total = sum(len(m["content"]) for m in messages)
    if total <= max_input_chars:
        return messages
    trimmed = list(messages)
    while len(trimmed) > 1:
        total = sum(len(m["content"]) for m in trimmed)
        if total <= max_input_chars:
            break
        trimmed.pop(0)
    return trimmed