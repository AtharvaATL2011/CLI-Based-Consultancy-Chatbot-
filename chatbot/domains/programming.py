"""
programming.py — Programming domain with Gemini 2.5 Flash code review.
Generation: GPT-4.1 via GitHub Models (free)
Review:     Gemini 2.5 Flash via Google AI Studio (free, native SDK)
"""

import os
import re
from google import genai
from google.genai import types
from chatbot.config import PROMPTS_DIR

# Force GEMINI_API_KEY — ignore GOOGLE_API_KEY conflict
# Force GEMINI_API_KEY — remove conflicting GOOGLE_API_KEY
os.environ.pop('GOOGLE_API_KEY', None)
_gemini_key = os.getenv("GEMINI_API_KEY")
_client = genai.Client(api_key=_gemini_key) if _gemini_key else None

_FALLBACK_PROMPT = """You are an expert programming mentor.
Write clean, well-commented code. Explain line by line when teaching.
For bugs, identify root cause first. Always follow best practices."""

_REVIEW_PROMPT = """You are a senior engineer doing a final production code review.

Fix any bugs, deprecated APIs, security issues, or bad practices you find.
Pay special attention based on the code type:

For Python/FastAPI:
- FastAPI form fields must use Form(...) not Depends()
- Pillow 10+: use font.getbbox() not draw.textsize()
- OpenAI SDK 1.0+: use openai.chat.completions.create() not openai.ChatCompletion.create()
- CORS: never combine allow_origins=["*"] with allow_credentials=True
- Always wrap Pillow calls in asyncio.run_in_executor()
- Validate file size at the START of every upload handler
- Secrets must come from os.getenv() with RuntimeError if missing
- pydantic v2: import BaseSettings from pydantic_settings not pydantic
- Pin all requirements versions with >=

For React/JavaScript:
- Every fetch() must have try/catch/finally with res.ok check
- Show errors inline not with alert()
- Validate file size client-side before uploading
- API URL must come from import.meta.env.VITE_API_URL

For Docker:
- Use named volumes not bind mounts for uploads
- Use env_file:.env not hardcoded secrets
- Internal service URLs use service name not localhost
- Vite CMD must include --host 0.0.0.0
- Add depends_on for service ordering

CRITICAL: Return ONLY the complete corrected code.
Nothing else. No explanation. No markdown. Just the code."""


def get_system_prompt() -> str:
    prompt_file = PROMPTS_DIR / "programming.txt"
    if prompt_file.exists():
        return prompt_file.read_text(encoding="utf-8").strip()
    return _FALLBACK_PROMPT


def _extract_text(response) -> str | None:
    """
    Safely extract text from Gemini response.
    Handles thinking mode where response.text can be None.
    """
    # Try direct text first
    if response.text:
        return response.text.strip()

    # Fall back to candidates — handles thinking mode
    try:
        if response.candidates:
            parts = response.candidates[0].content.parts
            # Filter out thinking parts, get only text parts
            text_parts = [p.text for p in parts if hasattr(p, 'text') and p.text]
            if text_parts:
                return "\n".join(text_parts).strip()
    except Exception:
        pass

    return None


def review_and_fix(code: str) -> str:
    """
    Two-layer review:
    Layer 1 — Gemini 2.5 Flash (smart, understands context)
    Layer 2 — Programmatic patches (guaranteed fallback)
    """
    if not _client:
        print("[review] No GEMINI_API_KEY found — running programmatic patches.")
        return _programmatic_fix(code)

    try:
        print("\n[review] Running Gemini 3.1 Flash review...")

        response = _client.models.generate_content(
            model="gemini-3.1-flash-lite-preview",
            contents=f"{_REVIEW_PROMPT}\n\n---CODE TO REVIEW---\n{code}\n---END CODE---",
            config=types.GenerateContentConfig(
                system_instruction=(
                    "You are a strict senior code reviewer. "
                    "Return ONLY the corrected code. "
                    "No explanations. No reasoning. No markdown fences. "
                    "Just the fixed code itself."
                ),
                temperature=0.0,
                max_output_tokens=8192,
            )
        )

        # Safe text extraction — handles thinking mode None
        fixed = _extract_text(response)

        if not fixed:
            print("[review] Gemini returned empty — running programmatic patches.")
            return _programmatic_fix(code)

        # Remove markdown fences if Gemini added them
        if fixed.startswith("```"):
            lines = fixed.split("\n")
            fixed = "\n".join(lines[1:-1]) if lines[-1].strip() == "```" else "\n".join(lines[1:])

        # Detect if Gemini returned explanation instead of code
        bad_indicators = [
            "Hmm,", "Wait,", "Let me", "I need to",
            "The user", "Looking at", "Please share",
            "No changes needed", "The code looks",
            "# 1. Form fields\n", "# Corrected code\n\n# 1.",
            "Here's the corrected", "Here is the corrected",
            "I've fixed", "I have fixed",
        ]
        if any(indicator in fixed for indicator in bad_indicators):
            print("[review] Gemini returned explanation — running programmatic patches.")
            return _programmatic_fix(code)

        if len(fixed) < 50:
            print("[review] Output too short — running programmatic patches.")
            return _programmatic_fix(code)

        print("[review] Gemini review complete.\n")

        # Always run programmatic patches on top of Gemini output
        return _programmatic_fix(fixed)

    except Exception as e:
        print(f"[review] Gemini failed ({e}) — running programmatic patches.")
        return _programmatic_fix(code)


def _programmatic_fix(code: str) -> str:
    """
    Deterministic patches for known recurring bugs.
    Always runs — either alone or after Gemini review.
    """
    fixes = []

    # Fix 1 — deprecated OpenAI API
    if "openai.ChatCompletion.create(" in code:
        code = code.replace(
            "openai.ChatCompletion.create(",
            "openai.chat.completions.create("
        )
        fixes.append("✅ Fixed deprecated ChatCompletion.create()")

    # Fix 2 — hardcoded API key fallback
    code = re.sub(
        r'os\.getenv\("OPENAI_API_KEY",\s*"[^"]*"\)',
        'os.getenv("OPENAI_API_KEY")',
        code
    )
    if 'os.getenv("OPENAI_API_KEY")' in code and "RuntimeError" not in code:
        code = code.replace(
            'openai.api_key = os.getenv("OPENAI_API_KEY")',
            'openai.api_key = os.getenv("OPENAI_API_KEY")\n'
            'if not openai.api_key:\n'
            '    raise RuntimeError("OPENAI_API_KEY environment variable is not set")'
        )
        fixes.append("✅ Fixed hardcoded API key fallback")

    # Fix 3 — Pillow blocking async
    if "add_caption(image_bytes" in code and "run_in_executor" not in code:
        code = code.replace(
            "buf = add_caption(image_bytes, caption)",
            "loop = asyncio.get_event_loop()\n"
            "    buf = await loop.run_in_executor(None, add_caption, image_bytes, caption)"
        )
        if "import asyncio" not in code:
            code = "import asyncio\n" + code
        fixes.append("✅ Fixed Pillow blocking — added run_in_executor")

    # Fix 4 — missing file size check
    if "image_bytes = await image.read()" in code and "MAX_SIZE" not in code:
        code = code.replace(
            "image_bytes = await image.read()",
            "MAX_SIZE = 10 * 1024 * 1024  # 10MB\n"
            "    image_bytes = await image.read(MAX_SIZE + 1)\n"
            "    if len(image_bytes) > MAX_SIZE:\n"
            '        raise HTTPException(400, "File too large — max 10MB")'
        )
        if "HTTPException" not in code:
            code = code.replace(
                "from fastapi import",
                "from fastapi import HTTPException, "
            )
        fixes.append("✅ Fixed missing file size validation")

    # Fix 5 — invalid import syntax
    if "import openai>=" in code:
        code = re.sub(r'import openai>=[\d.]+', 'import openai', code)
        fixes.append("✅ Fixed invalid import syntax")

    # Fix 6 — missing HTTPException import
    if "HTTPException" in code and "from fastapi import HTTPException" not in code:
        if "from fastapi import" in code and "HTTPException" not in code.split("from fastapi import")[1].split("\n")[0]:
            code = code.replace(
                "from fastapi import",
                "from fastapi import HTTPException, "
            )
            fixes.append("✅ Added missing HTTPException import")

    # Fix 7 — pin requirements versions
    replacements = {
        "\nfastapi\n": "\nfastapi>=0.110.0\n",
        "\nuvicorn\n": "\nuvicorn>=0.29.0\n",
        "\npillow\n": "\npillow>=10.0.0\n",
        "\nopenai\n": "\nopenai>=1.0.0\n",
        "\npython-multipart\n": "\npython-multipart>=0.0.9\n",
        "\nalembic\n": "\nalembic>=1.13.0\n",
        "\nredis\n": "\nredis>=5.0.0\n",
    }
    for old, new in replacements.items():
        if old in code:
            code = code.replace(old, new)

    if fixes:
        print("\n[programmatic-review] Patches applied:")
        for f in fixes:
            print(f"  {f}")
    else:
        print("\n[programmatic-review] No additional patches needed.")

    return code


def enrich_message(user_message: str) -> str:
    return user_message