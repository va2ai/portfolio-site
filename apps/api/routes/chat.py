"""Chat endpoint — simple conversation with the portfolio agent."""
from __future__ import annotations

import logging
import os
import time
import uuid
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from core.shared.config import settings

logging.getLogger("google_genai.types").setLevel(logging.ERROR)
logger = logging.getLogger(__name__)

router = APIRouter(tags=["chat"])

# In-memory session store
_sessions: dict[str, list[dict[str, Any]]] = {}

MAX_HISTORY = 40


class ChatRequest(BaseModel):
    message: str
    session_id: str = ""
    audience: str = ""  # recruiter | technical | client | (empty = auto-detect)


class ChatResponse(BaseModel):
    reply: str
    model: str
    session_id: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    latency_ms: float = 0.0


@router.post("/chat")
async def chat(req: ChatRequest):
    t0 = time.time()

    # Resolve API key
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or settings.google_api_key
    if not api_key:
        return ChatResponse(reply="Server configuration error: no API key set.", model="none")

    # Get or create session
    sid = req.session_id or str(uuid.uuid4())
    history = _sessions.setdefault(sid, [])

    # Load agent
    from core.agents.registry import agent_registry
    agent = agent_registry.get("portfolio")

    # Build system prompt with audience hint
    system_prompt = agent.system_prompt
    if req.audience:
        system_prompt += f"\n\n## Current Visitor\nThe visitor has identified as: {req.audience}. Adapt your responses accordingly."

    # Build conversation contents for Gemini
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)
    model = agent.model or settings.default_model

    # Build contents list from history + new message
    contents = []
    for msg in history:
        contents.append(types.Content(
            role=msg["role"],
            parts=[types.Part.from_text(text=msg["text"])],
        ))
    contents.append(types.Content(
        role="user",
        parts=[types.Part.from_text(text=req.message)],
    ))

    try:
        response = client.models.generate_content(
            model=model,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.7,
                max_output_tokens=1024,
            ),
        )

        reply_text = response.text or "I couldn't generate a response. Please try again."
        input_tokens = getattr(response.usage_metadata, "prompt_token_count", 0) or 0
        output_tokens = getattr(response.usage_metadata, "candidates_token_count", 0) or 0

    except Exception as e:
        logger.error(f"Gemini API error: {e}", exc_info=True)
        reply_text = "I'm having trouble connecting right now. Please try again in a moment."
        input_tokens = 0
        output_tokens = 0

    # Save to session history
    history.append({"role": "user", "text": req.message})
    history.append({"role": "model", "text": reply_text})

    # Truncate
    if len(history) > MAX_HISTORY:
        _sessions[sid] = history[-MAX_HISTORY:]

    latency = (time.time() - t0) * 1000

    return ChatResponse(
        reply=reply_text,
        model=model,
        session_id=sid,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        latency_ms=round(latency, 1),
    )


@router.delete("/chat/{session_id}")
async def clear_session(session_id: str):
    _sessions.pop(session_id, None)
    return {"status": "cleared"}


# ─── Demo endpoint (Hybrid vs Prompt-Only comparison) ─────────────

class DemoRequest(BaseModel):
    naive_system: str
    naive_user: str
    hybrid_system: str
    hybrid_user: str


@router.post("/demo")
async def demo_compare(req: DemoRequest):
    """Run two LLM calls in parallel: naive (prompt-only) and hybrid (constrained)."""
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or settings.google_api_key
    if not api_key:
        return {"error": "Server configuration error: no API key set."}

    from google import genai
    from google.genai import types
    import asyncio

    client = genai.Client(api_key=api_key)
    model = "gemini-3-flash-preview"

    async def call_gemini(system: str, user: str) -> str:
        try:
            response = client.models.generate_content(
                model=model,
                contents=[types.Content(role="user", parts=[types.Part.from_text(text=user)])],
                config=types.GenerateContentConfig(
                    system_instruction=system,
                    temperature=0.7,
                    max_output_tokens=600,
                ),
            )
            return response.text or "No response."
        except Exception as e:
            logger.error(f"Demo Gemini error: {e}", exc_info=True)
            return f"Error: {e}"

    naive_result, hybrid_result = await asyncio.gather(
        call_gemini(req.naive_system, req.naive_user),
        call_gemini(req.hybrid_system, req.hybrid_user),
    )

    return {"naive": naive_result, "hybrid": hybrid_result}
