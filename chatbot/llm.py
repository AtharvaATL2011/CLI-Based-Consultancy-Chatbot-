"""
llm.py — wrapper around OpenRouter API with automatic retry on rate limits.
"""

import time
from openai import OpenAI, RateLimitError
from chatbot.config import ANTHROPIC_API_KEY, MODEL, TEMPERATURE, MAX_TOKENS

_client = OpenAI(
    api_key=ANTHROPIC_API_KEY,
    base_url="https://openrouter.ai/api/v1",
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

    for attempt in range(retries):
        try:
            response = _client.chat.completions.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=full_messages,
                extra_headers={
                    "HTTP-Referer": "https://github.com/AtharvaATL2011/CLI-Based-Consultancy-Chatbot-",
                    "X-Title": "MultiMind Chatbot",
                },
            )
            return response.choices[0].message.content

        except RateLimitError:
            if attempt < retries - 1:
                wait = retry_delay * (attempt + 1)
                print(f"\n[Rate limited] Waiting {wait}s before retry ({attempt+1}/{retries-1})...")
                time.sleep(wait)
            else:
                return (
                    "The AI service is temporarily rate-limited. "
                    "Please wait 30 seconds and try again. "
                    "This is a free tier limitation."
                )

        except Exception as e:
            return f"I ran into an issue: {e}\nPlease check your API key and try again."


def quick_classify(prompt: str) -> str:
    """Lightweight call for intent routing — low tokens, deterministic."""
    return chat(
        messages=[{"role": "user", "content": prompt}],
        system_prompt="You are a classifier. Respond with exactly one word, nothing else.",
        max_tokens=10,
        temperature=0.0,
        retries=2,
        retry_delay=3,
    )