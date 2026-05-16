from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import time

from chatbot.memory import Memory
from chatbot.engine import Engine

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Single memory instance persists across all requests (like the CLI does)
memory = Memory()

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat(req: ChatRequest):
    import asyncio, re
    start = time.time()
    engine = Engine(memory=memory)
    response, domain = await asyncio.to_thread(engine.respond, req.message)

    # ── Force-wrap any unfenced code blocks ──────────────────────────
    # If response has no fences but looks like code, wrap the whole thing
    if domain == "programming" and "```" not in response:
        lines = response.split("\n")
        # Find where code starts (first indented or keyword line)
        code_start = next((i for i, l in enumerate(lines)
                          if l.startswith("    ") or l.startswith("\t")
                          or any(l.startswith(k) for k in ["import","def","class","from"])), None)
        if code_start is not None:
            text_before = "\n".join(lines[:code_start]).strip()
            code = "\n".join(lines[code_start:]).strip()
            response = f"{text_before}\n\n```python\n{code}\n```" if text_before else f"```python\n{code}\n```"
    # ─────────────────────────────────────────────────────────────────

    return {
        "response": response,
        "domain": domain,
        "latency": round(time.time() - start, 2),
        "score": 0,
        "confidence": 0.9,
        "tokens": 0,
        "pipeline": [
            [domain, "routed"],
            ["gpt-4.1", "generated"],
            ["gemini", "reviewed"] if domain == "programming" else ["post-process", "done"],
            ["sqlite", "saved"],
        ]
    }