from __future__ import annotations

import os
from typing import Any

from pydantic import BaseModel

from ..base import BaseTool, ToolOutput


class TavilySearchInput(BaseModel):
    query: str
    max_results: int = 5
    search_depth: str = "basic"  # basic | advanced
    include_answer: bool = True
    topic: str = "general"  # general | news


class TavilySearchTool(BaseTool):
    name = "tavily_search"
    description = "Search the web using Tavily AI search engine. Returns relevant results with AI-generated answers."
    safety_level = "safe"
    timeout_seconds = 30

    def __init__(self, api_key: str | None = None) -> None:
        self._api_key = api_key or os.environ.get("TAVILY_API_KEY", "")

    def input_schema(self) -> type[BaseModel]:
        return TavilySearchInput

    async def execute(self, input_data: BaseModel) -> ToolOutput:
        if not self._api_key:
            return ToolOutput(success=False, error="TAVILY_API_KEY not configured")

        try:
            from tavily import TavilyClient

            client = TavilyClient(api_key=self._api_key)
            response = client.search(
                query=input_data.query,
                max_results=input_data.max_results,
                search_depth=input_data.search_depth,
                include_answer=input_data.include_answer,
                topic=input_data.topic,
            )

            results = []
            for r in response.get("results", []):
                results.append({
                    "title": r.get("title", ""),
                    "url": r.get("url", ""),
                    "content": r.get("content", ""),
                    "score": r.get("score", 0),
                })

            return ToolOutput(
                success=True,
                result={
                    "answer": response.get("answer", ""),
                    "results": results,
                    "response_time": response.get("response_time", 0),
                },
            )
        except Exception as e:
            return ToolOutput(success=False, error=str(e))
