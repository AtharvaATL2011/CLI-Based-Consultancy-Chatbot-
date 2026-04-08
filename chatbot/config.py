"""
config.py — loads environment variables and exposes settings.
All other modules import from here; nothing reads .env directly.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")


def _require(key: str) -> str:
    value = os.getenv(key)
    if not value:
        raise EnvironmentError(
            f"\n[config] Missing required environment variable: {key}\n"
            f"         Copy .env.example to .env and fill in your values.\n"
        )
    return value


# API
ANTHROPIC_API_KEY: str = _require("ANTHROPIC_API_KEY")
MODEL: str = os.getenv("MODEL", "claude-sonnet-4-20250514")
TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.7"))
MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "1024"))

# Storage
DB_PATH: str = os.getenv("DB_PATH", "chatbot_memory.db")

# Domains
VALID_DOMAINS = {"education", "healthcare", "finance", "general"}
DEFAULT_DOMAIN = "general"

# Prompts directory
PROMPTS_DIR: Path = Path(__file__).parent.parent / "prompts"