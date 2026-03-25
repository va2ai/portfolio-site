from __future__ import annotations

import os

from fastapi import APIRouter
from pydantic import BaseModel

from core.shared.config import settings

router = APIRouter(tags=["search"])


class SearchRequest(BaseModel):
    query: str
    max_results: int = 5
    search_depth: str = "basic"
    include_answer: bool = True


@router.post("/search")
async def search(req: SearchRequest):
    api_key = os.environ.get("TAVILY_API_KEY", "") or settings.tavily_api_key
    if not api_key:
        return {"error": "TAVILY_API_KEY not set"}

    from tavily import TavilyClient

    client = TavilyClient(api_key=api_key)
    response = client.search(
        query=req.query,
        max_results=req.max_results,
        search_depth=req.search_depth,
        include_answer=req.include_answer,
    )

    return {
        "answer": response.get("answer", ""),
        "results": [
            {
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "content": r.get("content", ""),
                "score": r.get("score", 0),
            }
            for r in response.get("results", [])
        ],
        "response_time": response.get("response_time", 0),
    }
