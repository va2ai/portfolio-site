from __future__ import annotations

import logging
import os
import time
import uuid
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from core.shared.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(tags=["chat"])

# In-memory session store (per server process)
_sessions: dict[str, list[dict[str, Any]]] = {}


class ChatRequest(BaseModel):
    message: str
    model: str = ""
    system: str = "You are a helpful AI assistant. You have access to a tavily_search tool for searching the web. When the user asks about current events, recent information, or anything you're unsure about, use the tavily_search tool to find accurate answers."
    session_id: str = ""


class ChatResponse(BaseModel):
    reply: str
    model: str
    session_id: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    latency_ms: float = 0.0
    tool_calls: list[dict[str, Any]] = []


class EditRequest(BaseModel):
    session_id: str
    index: int
    text: str


class DeleteRequest(BaseModel):
    session_id: str
    index: int


class ClearRequest(BaseModel):
    session_id: str


def _get_tavily_tool_declaration():
    from google.genai import types

    return types.Tool(
        function_declarations=[
            types.FunctionDeclaration(
                name="tavily_search",
                description="Search the web for current information using Tavily. Use this when the user asks about recent events, facts you're unsure about, or anything that benefits from real-time web data.",
                parameters=types.Schema(
                    type="OBJECT",
                    properties={
                        "query": types.Schema(type="STRING", description="The search query"),
                        "max_results": types.Schema(type="INTEGER", description="Number of results (1-10, default 5)"),
                    },
                    required=["query"],
                ),
            ),
        ]
    )


def _execute_tavily(query: str, max_results: int = 5) -> dict[str, Any]:
    tavily_key = os.environ.get("TAVILY_API_KEY", "") or settings.tavily_api_key
    if not tavily_key:
        return {"error": "TAVILY_API_KEY not set"}

    try:
        from tavily import TavilyClient

        client = TavilyClient(api_key=tavily_key)
        response = client.search(
            query=query,
            max_results=max_results,
        )
        logger.info(f"Tavily search OK: query='{query}', results={len(response.get('results', []))}")

        results = []
        for r in response.get("results", []):
            results.append({
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "content": r.get("content", ""),
            })

        return {
            "answer": response.get("answer") or "",
            "results": results,
        }
    except Exception as e:
        logger.error(f"Tavily search failed: {type(e).__name__}: {e}", exc_info=True)
        return {"error": str(e)}


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    model = req.model or settings.default_model
    api_key = os.environ.get("GEMINI_API_KEY", "") or os.environ.get("GOOGLE_API_KEY", "") or settings.google_api_key
    session_id = req.session_id or str(uuid.uuid4())

    if not api_key:
        return ChatResponse(
            reply="[Mock] No GOOGLE_API_KEY found in env or .env. Your message was: " + req.message,
            model="mock",
            session_id=session_id,
        )

    if session_id not in _sessions:
        _sessions[session_id] = []

    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)

    # Build tools list
    tools = []
    tavily_key = os.environ.get("TAVILY_API_KEY", "") or settings.tavily_api_key
    if tavily_key:
        tools.append(_get_tavily_tool_declaration())

    # Build contents from session history + new message
    # We keep session history as simple dicts for text messages only.
    # Function call rounds are handled within a single request and not persisted.
    contents = []
    for m in _sessions[session_id]:
        contents.append(types.Content(
            role=m["role"],
            parts=[types.Part.from_text(text=m["text"])],
        ))
    # Add new user message
    contents.append(types.Content(
        role="user",
        parts=[types.Part.from_text(text=req.message)],
    ))

    start = time.monotonic()
    tool_calls_made = []

    try:
        response = client.models.generate_content(
            model=model,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=req.system,
                tools=tools if tools else None,
            ),
        )

        # Handle function calls (tool use loop, max 3 rounds)
        for _ in range(3):
            if not response.candidates or not response.candidates[0].content.parts:
                break

            function_calls = [p for p in response.candidates[0].content.parts if p.function_call]
            if not function_calls:
                break

            # Add model's function call response to contents
            contents.append(response.candidates[0].content)

            # Execute each function call and build response parts
            fn_response_parts = []
            for fc in function_calls:
                fn_name = fc.function_call.name
                fn_args = dict(fc.function_call.args) if fc.function_call.args else {}

                if fn_name == "tavily_search":
                    result = _execute_tavily(
                        query=fn_args.get("query", ""),
                        max_results=int(fn_args.get("max_results", 5)),
                    )
                    tool_calls_made.append({"tool": "tavily_search", "query": fn_args.get("query", "")})
                else:
                    result = {"error": f"Unknown function: {fn_name}"}

                fn_response_parts.append(
                    types.Part.from_function_response(name=fn_name, response=result)
                )

            # Add function results
            contents.append(types.Content(role="user", parts=fn_response_parts))

            # Get next response
            response = client.models.generate_content(
                model=model,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=req.system,
                    tools=tools if tools else None,
                ),
            )

        elapsed = (time.monotonic() - start) * 1000
        reply_text = response.text or ""

        # Save to session as simple dicts (text only, no SDK objects)
        _sessions[session_id].append({"role": "user", "text": req.message})
        _sessions[session_id].append({"role": "model", "text": reply_text})

        # Keep history manageable
        if len(_sessions[session_id]) > 40:
            _sessions[session_id] = _sessions[session_id][-40:]

        return ChatResponse(
            reply=reply_text,
            model=model,
            session_id=session_id,
            input_tokens=getattr(response.usage_metadata, "prompt_token_count", 0) or 0 if response.usage_metadata else 0,
            output_tokens=getattr(response.usage_metadata, "candidates_token_count", 0) or 0 if response.usage_metadata else 0,
            latency_ms=elapsed,
            tool_calls=tool_calls_made,
        )

    except Exception as e:
        elapsed = (time.monotonic() - start) * 1000
        logger.error(f"Chat error: {e}")
        return ChatResponse(
            reply=f"Error: {str(e)}",
            model=model,
            session_id=session_id,
            latency_ms=elapsed,
        )


@router.get("/history")
async def get_history(session_id: str):
    history = _sessions.get(session_id, [])
    return {
        "session_id": session_id,
        "messages": [
            {"index": i, "role": m["role"], "text": m["text"]}
            for i, m in enumerate(history)
        ],
    }


@router.post("/history/edit")
async def edit_message(req: EditRequest):
    history = _sessions.get(req.session_id)
    if not history or req.index < 0 or req.index >= len(history):
        return {"error": "Invalid session or index"}

    history[req.index]["text"] = req.text
    _sessions[req.session_id] = history[: req.index + 1]
    return {"ok": True, "remaining": len(_sessions[req.session_id])}


@router.post("/history/delete")
async def delete_message(req: DeleteRequest):
    history = _sessions.get(req.session_id)
    if not history or req.index < 0 or req.index >= len(history):
        return {"error": "Invalid session or index"}

    _sessions[req.session_id].pop(req.index)
    return {"ok": True, "remaining": len(_sessions[req.session_id])}


@router.post("/history/clear")
async def clear_history(req: ClearRequest):
    _sessions.pop(req.session_id, None)
    return {"ok": True}
