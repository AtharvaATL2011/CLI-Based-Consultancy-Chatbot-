# check_gemini.py
from google import genai
from google.genai import types
import os
from dotenv import load_dotenv

load_dotenv()

# Force GEMINI_API_KEY — remove conflicting key
os.environ.pop('GOOGLE_API_KEY', None)

api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    print('❌ GEMINI_API_KEY not found in .env')
    exit()

client = genai.Client(api_key=api_key)

try:
    # Use gemini-2.0-flash for health check — no thinking mode, faster response
    response = client.models.generate_content(
    model='gemini-3.1-flash-lite-preview',  # most generous free tier
    contents='Reply with exactly one word: hello',
    config=types.GenerateContentConfig(
        max_output_tokens=50,
        temperature=0.0,
    )
)

    # Safely extract text
    text = None
    if response.text:
        text = response.text.strip()
    elif response.candidates:
        try:
            parts = response.candidates[0].content.parts
            text_parts = [p.text for p in parts if hasattr(p, 'text') and p.text]
            text = " ".join(text_parts).strip() if text_parts else None
        except Exception:
            text = None

    if text:
        print(f'✅ Gemini is available — safe to run chatbot')
        print(f'Response: {text}')
    else:
        print('❌ Gemini returned empty — server overloaded, wait 5 minutes')

except Exception as e:
    error = str(e)
    if "503" in error or "UNAVAILABLE" in error:
        print('❌ Gemini server busy — wait 5 minutes and try again')
    elif "429" in error or "RESOURCE_EXHAUSTED" in error:
        print('❌ Rate limit hit — wait 1 minute and try again')
    elif "401" in error or "API_KEY" in error.upper():
        print('❌ Invalid API key — check GEMINI_API_KEY in .env')
    else:
        print(f'❌ Gemini error: {error}')