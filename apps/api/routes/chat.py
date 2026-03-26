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

NAIVE_MODEL = "gemini-2.5-flash"        # capable model, no guardrails
HYBRID_MODEL = "gemini-2.0-flash-lite"  # cheapest model, with hybrid architecture


class DemoRequest(BaseModel):
    naive_system: str
    naive_user: str
    hybrid_system: str
    hybrid_user: str


@router.post("/demo")
async def demo_compare(req: DemoRequest):
    """Run two LLM calls in parallel: expensive model raw vs cheap model with hybrid architecture."""
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or settings.google_api_key
    if not api_key:
        return {"error": "Server configuration error: no API key set."}

    from google import genai
    from google.genai import types
    import asyncio

    client = genai.Client(api_key=api_key)

    async def call_gemini(model: str, system: str, user: str) -> str:
        try:
            config = types.GenerateContentConfig(
                system_instruction=system,
                temperature=0.7,
                max_output_tokens=2048,
            )
            # Minimize thinking for 2.5 Pro (it returns thinking blocks that break .text)
            if "2.5" in model:
                config.thinking_config = types.ThinkingConfig(thinking_budget=1024)

            response = client.models.generate_content(
                model=model,
                contents=[types.Content(role="user", parts=[types.Part.from_text(text=user)])],
                config=config,
            )
            # Extract text from all non-thought parts
            text_parts = []
            for candidate in (response.candidates or []):
                for part in (candidate.content.parts or []):
                    if hasattr(part, "text") and part.text and not getattr(part, "thought", False):
                        text_parts.append(part.text)
            return "\n".join(text_parts) or "No response."
        except Exception as e:
            logger.error(f"Demo Gemini error ({model}): {e}", exc_info=True)
            return f"Error: {e}"

    naive_result, hybrid_result = await asyncio.gather(
        call_gemini(NAIVE_MODEL, req.naive_system, req.naive_user),
        call_gemini(HYBRID_MODEL, req.hybrid_system, req.hybrid_user),
    )

    return {
        "naive": naive_result,
        "hybrid": hybrid_result,
        "naive_model": NAIVE_MODEL,
        "hybrid_model": HYBRID_MODEL,
    }
