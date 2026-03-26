from __future__ import annotations

import os
from typing import Any

from pydantic import BaseModel

from ..base import BaseTool, ToolOutput


class ExaSearchInput(BaseModel):
    query: str
    num_results: int = 5
    search_type: str = "auto"  # auto | instant | fast | deep
    category: str = ""  # company | people | research paper | news | personal site | financial report


class ExaSearchTool(BaseTool):
    name = "exa_search"
    description = "Search the web using Exa AI — semantic neural search with content extraction. Best for research papers, companies, people, and deep topical searches."
    safety_level = "safe"
    timeout_seconds = 60

    def __init__(self, api_key: str | None = None) -> None:
        self._api_key = api_key or os.environ.get("EXA_API_KEY", "")

    def input_schema(self) -> type[BaseModel]:
        return ExaSearchInput

    async def execute(self, input_data: BaseModel) -> ToolOutput:
        if not self._api_key:
            return ToolOutput(success=False, error="EXA_API_KEY not configured")

        try:
            from exa_py import Exa

            exa = Exa(api_key=self._api_key)

            kwargs = {
                "query": input_data.query,
                "type": input_data.search_type,
                "num_results": input_data.num_results,
                "contents": {
                    "highlights": {"max_characters": 4000}
                },
            }

            if input_data.category:
                kwargs["category"] = input_data.category

            result = exa.search(**kwargs)

            results = []
            for r in result.results:
                results.append({
                    "title": getattr(r, "title", ""),
                    "url": getattr(r, "url", ""),
                    "highlights": getattr(r, "highlights", []),
                    "score": getattr(r, "score", 0),
                })

            return ToolOutput(success=True, result={"results": results})
        except Exception as e:
            return ToolOutput(success=False, error=str(e))
