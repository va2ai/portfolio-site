from __future__ import annotations

import datetime
import logging
import math
import os
import time
import uuid
import warnings
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from core.shared.config import settings

# Suppress noisy SDK warnings
logging.getLogger("google_genai.types").setLevel(logging.ERROR)
logging.getLogger("praw").setLevel(logging.ERROR)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["chat"])

# In-memory session store (per server process)
_sessions: dict[str, list[dict[str, Any]]] = {}

# Live tool activity tracker — updated during tool loop, polled by frontend
_live_activity: dict[str, dict[str, Any]] = {}

# ─── Tool calling modes ───────────────────────────────────────────────
# AUTO  — model decides whether to call tools (default)
# ANY   — model MUST call at least one tool
# NONE  — tools are provided for context but model won't call them
TOOL_MODE = "AUTO"
MAX_TOOL_ROUNDS = 10  # allow deep research chains


# ─── Request / Response models ────────────────────────────────────────

DEFAULT_SYSTEM = (
    "You are a helpful AI assistant with access to tools. "
    "Use tavily_search for web lookups, calculator for math, "
    "and get_current_datetime for date/time questions. "
    "You can call multiple tools in parallel when the user's request involves independent sub-tasks. "
    "You can also chain tools sequentially — use the output of one tool as input to another."
)


class ChatRequest(BaseModel):
    message: str
    model: str = ""
    system: str = ""
    session_id: str = ""
    tool_mode: str = "AUTO"  # AUTO | ANY | NONE
    agent: str = ""  # agent name from registry, overrides system/model
    google_search: bool = False  # enable native Google Search grounding
    research_depth: int = 3  # max tool rounds (1-10)


class ToolCallInfo(BaseModel):
    tool: str
    args: dict[str, Any] = {}
    result_preview: str = ""
    success: bool = True


class ToolStep(BaseModel):
    round: int
    calls: list[ToolCallInfo] = []


class GroundingSource(BaseModel):
    title: str = ""
    url: str = ""


class ChatResponse(BaseModel):
    reply: str
    model: str
    session_id: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    latency_ms: float = 0.0
    tool_calls: list[dict[str, Any]] = []
    tool_steps: list[ToolStep] = []
    tool_rounds: int = 0
    grounding_sources: list[GroundingSource] = []
    search_queries: list[str] = []


class EditRequest(BaseModel):
    session_id: str
    index: int
    text: str


class DeleteRequest(BaseModel):
    session_id: str
    index: int


class ClearRequest(BaseModel):
    session_id: str


# ─── Tool declarations ────────────────────────────────────────────────

def _build_tool_declarations():
    """Build all function declarations as a single Tool object.

    Grouping them in one Tool enables parallel calling — the model can
    invoke multiple functions from the same Tool in a single response.
    """
    from google.genai import types

    return types.Tool(
        function_declarations=[
            # 1. Web search
            types.FunctionDeclaration(
                name="tavily_search",
                description=(
                    "Search the web for current information. Use for news, facts, "
                    "recent events, prices, weather, or anything that benefits from "
                    "real-time data. Can be called multiple times in parallel with "
                    "different queries for multi-topic research."
                ),
                parameters=types.Schema(
                    type="OBJECT",
                    properties={
                        "query": types.Schema(type="STRING", description="The search query"),
                        "max_results": types.Schema(type="INTEGER", description="Number of results, 1-10 (default 5)"),
                        "topic": types.Schema(type="STRING", description="Search topic: 'general' or 'news' (default 'general')"),
                    },
                    required=["query"],
                ),
            ),
            # 2. Calculator — supports expressions, unit conversions, percentages
            types.FunctionDeclaration(
                name="calculator",
                description=(
                    "Evaluate mathematical expressions. Supports arithmetic, "
                    "percentages, exponents, sqrt, trig functions, log, abs, "
                    "round, min, max, pi, e. Use for any computation the user "
                    "asks about. Chain with other tools for data-driven calculations."
                ),
                parameters=types.Schema(
                    type="OBJECT",
                    properties={
                        "expression": types.Schema(
                            type="STRING",
                            description="Math expression to evaluate, e.g. '(15000 * 0.06) / 12' or 'sqrt(144) + pi'"
                        ),
                    },
                    required=["expression"],
                ),
            ),
            # 3. Date/time
            types.FunctionDeclaration(
                name="get_current_datetime",
                description=(
                    "Get the current date, time, day of week, or timezone info. "
                    "Use when the user asks what day/time it is, or when you need "
                    "the current date for context in other tool calls."
                ),
                parameters=types.Schema(
                    type="OBJECT",
                    properties={
                        "timezone": types.Schema(
                            type="STRING",
                            description="Timezone name like 'US/Eastern', 'UTC', 'Europe/London' (default: UTC)"
                        ),
                        "format": types.Schema(
                            type="STRING",
                            description="'full' for date+time+day, 'date' for date only, 'time' for time only (default: 'full')"
                        ),
                    },
                ),
            ),
            # 4. Exa semantic search
            types.FunctionDeclaration(
                name="exa_search",
                description=(
                    "Semantic neural search via Exa AI. Best for finding research papers, "
                    "companies, people, news articles, and topical deep dives. "
                    "Returns content highlights. Use alongside tavily_search for "
                    "comprehensive coverage — Exa excels at semantic relevance while "
                    "Tavily excels at recency. Can be called in parallel with tavily_search."
                ),
                parameters=types.Schema(
                    type="OBJECT",
                    properties={
                        "query": types.Schema(type="STRING", description="Semantic search query — describe what you're looking for naturally"),
                        "num_results": types.Schema(type="INTEGER", description="Number of results, 1-10 (default 5)"),
                        "category": types.Schema(type="STRING", description="Optional filter: 'company', 'people', 'research paper', 'news', 'personal site', 'financial report'"),
                    },
                    required=["query"],
                ),
            ),
            # 5. URL content reader
            types.FunctionDeclaration(
                name="read_url",
                description=(
                    "Fetch and extract the main text content from a URL. "
                    "Use when the user provides a link and wants a summary, "
                    "or when you need to read a webpage for information. "
                    "Can be called in parallel with multiple URLs."
                ),
                parameters=types.Schema(
                    type="OBJECT",
                    properties={
                        "url": types.Schema(type="STRING", description="The URL to fetch"),
                    },
                    required=["url"],
                ),
            ),
            # 6. Reddit search
            types.FunctionDeclaration(
                name="reddit_search",
                description=(
                    "Search Reddit for discussions, opinions, experiences, and community knowledge. "
                    "Best for real user experiences, product reviews, troubleshooting, advice threads. "
                    "Specify a subreddit to narrow results, or leave empty to search all of Reddit."
                ),
                parameters=types.Schema(
                    type="OBJECT",
                    properties={
                        "query": types.Schema(type="STRING", description="Search query"),
                        "subreddit": types.Schema(type="STRING", description="Subreddit name without r/ (e.g. 'personalfinance'). Empty to search all."),
                        "sort": types.Schema(type="STRING", description="Sort: 'relevance', 'hot', 'top', 'new', 'comments' (default 'relevance')"),
                        "time_filter": types.Schema(type="STRING", description="Time: 'all', 'day', 'week', 'month', 'year' (default 'all')"),
                        "limit": types.Schema(type="INTEGER", description="Max results 1-25 (default 10)"),
                    },
                    required=["query"],
                ),
            ),
            # 7. Reddit read post
            types.FunctionDeclaration(
                name="reddit_read_post",
                description=(
                    "Read a full Reddit post and its top comments. "
                    "Use after reddit_search to dive into the most relevant threads."
                ),
                parameters=types.Schema(
                    type="OBJECT",
                    properties={
                        "url": types.Schema(type="STRING", description="Full Reddit post URL"),
                        "comment_limit": types.Schema(type="INTEGER", description="Max comments to return (default 10)"),
                    },
                    required=["url"],
                ),
            ),
            # 8. Reddit subreddit browse
            types.FunctionDeclaration(
                name="reddit_subreddit",
                description=(
                    "Browse a subreddit's current posts by hot, new, top, or rising. "
                    "Use to see what a community is actively discussing right now."
                ),
                parameters=types.Schema(
                    type="OBJECT",
                    properties={
                        "subreddit": types.Schema(type="STRING", description="Subreddit name without r/"),
                        "sort": types.Schema(type="STRING", description="Sort: 'hot', 'new', 'top', 'rising' (default 'hot')"),
                        "time_filter": types.Schema(type="STRING", description="For 'top' sort: 'day', 'week', 'month', 'year', 'all'"),
                        "limit": types.Schema(type="INTEGER", description="Max posts (default 10)"),
                    },
                    required=["subreddit"],
                ),
            ),
            # 9. Delegate to another agent
            types.FunctionDeclaration(
                name="delegate_to_agent",
                description=(
                    "Delegate a sub-task to another specialized agent. The agent runs independently "
                    "with its own tools and system prompt, then returns its full research output. "
                    "Available agents: 'reddit' (mines Reddit for community discussions, opinions, experiences), "
                    "'research' (deep web research with Tavily + Exa, structured findings with sources). "
                    "Use this when you need to delegate a sub-task to a specialist."
                ),
                parameters=types.Schema(
                    type="OBJECT",
                    properties={
                        "agent_name": types.Schema(type="STRING", description="Agent to delegate to: 'reddit'"),
                        "task": types.Schema(type="STRING", description="The research question or task to delegate"),
                    },
                    required=["agent_name", "task"],
                ),
            ),
        ]
    )


# ─── Tool executors ───────────────────────────────────────────────────

def _execute_tavily(query: str, max_results: int = 5, topic: str = "general") -> dict[str, Any]:
    tavily_key = os.environ.get("TAVILY_API_KEY", "") or settings.tavily_api_key
    if not tavily_key:
        return {"error": "TAVILY_API_KEY not set"}
    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=tavily_key)
        response = client.search(query=query, max_results=max_results, topic=topic)
        logger.info(f"tavily_search OK: query='{query}', results={len(response.get('results', []))}")
        return {
            "answer": response.get("answer") or "",
            "results": [
                {"title": r.get("title", ""), "url": r.get("url", ""), "content": r.get("content", "")}
                for r in response.get("results", [])
            ],
        }
    except Exception as e:
        logger.error(f"tavily_search failed: {e}", exc_info=True)
        return {"error": str(e)}


def _execute_exa(query: str, num_results: int = 5, category: str = "") -> dict[str, Any]:
    exa_key = os.environ.get("EXA_API_KEY", "") or settings.exa_api_key
    if not exa_key:
        return {"error": "EXA_API_KEY not set"}
    try:
        from exa_py import Exa
        exa = Exa(api_key=exa_key)

        kwargs = {
            "query": query,
            "type": "auto",
            "num_results": num_results,
            "contents": {"highlights": {"max_characters": 4000}},
        }
        if category:
            kwargs["category"] = category

        result = exa.search(**kwargs)
        logger.info(f"exa_search OK: query='{query}', results={len(result.results)}")

        return {
            "results": [
                {
                    "title": getattr(r, "title", ""),
                    "url": getattr(r, "url", ""),
                    "highlights": getattr(r, "highlights", []),
                    "score": getattr(r, "score", 0),
                }
                for r in result.results
            ],
        }
    except Exception as e:
        logger.error(f"exa_search failed: {e}", exc_info=True)
        return {"error": str(e)}


def _execute_calculator(expression: str) -> dict[str, Any]:
    """Safe math evaluator with common functions."""
    safe_names = {
        "abs": abs, "round": round, "min": min, "max": max,
        "sqrt": math.sqrt, "pow": math.pow, "log": math.log, "log10": math.log10, "log2": math.log2,
        "sin": math.sin, "cos": math.cos, "tan": math.tan,
        "asin": math.asin, "acos": math.acos, "atan": math.atan,
        "ceil": math.ceil, "floor": math.floor,
        "pi": math.pi, "e": math.e, "inf": math.inf,
    }
    try:
        # Only allow safe characters + function names
        result = eval(expression, {"__builtins__": {}}, safe_names)  # noqa: S307
        logger.info(f"calculator OK: '{expression}' = {result}")
        return {"expression": expression, "result": result}
    except Exception as e:
        logger.error(f"calculator failed: '{expression}': {e}")
        return {"expression": expression, "error": str(e)}


def _execute_get_datetime(timezone: str = "UTC", fmt: str = "full") -> dict[str, Any]:
    """Get current date/time in specified timezone."""
    try:
        from zoneinfo import ZoneInfo
        tz = ZoneInfo(timezone)
    except Exception:
        from datetime import timezone as dt_tz
        tz = dt_tz.utc
        timezone = "UTC"

    now = datetime.datetime.now(tz)

    if fmt == "date":
        return {"date": now.strftime("%Y-%m-%d"), "day_of_week": now.strftime("%A"), "timezone": timezone}
    elif fmt == "time":
        return {"time": now.strftime("%H:%M:%S"), "timezone": timezone}
    else:
        return {
            "datetime": now.isoformat(),
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M:%S"),
            "day_of_week": now.strftime("%A"),
            "timezone": timezone,
        }


def _execute_read_url(url: str) -> dict[str, Any]:
    """Fetch URL content and return as text."""
    try:
        import httpx
        resp = httpx.get(url, timeout=15, follow_redirects=True, headers={"User-Agent": "AI-Agent-Platform/1.0"})
        resp.raise_for_status()
        content_type = resp.headers.get("content-type", "")

        if "text/html" in content_type:
            # Strip HTML tags for a rough text extraction
            import re
            text = re.sub(r'<script[^>]*>.*?</script>', '', resp.text, flags=re.DOTALL)
            text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
            text = re.sub(r'<[^>]+>', ' ', text)
            text = re.sub(r'\s+', ' ', text).strip()
            # Truncate to avoid massive responses
            if len(text) > 8000:
                text = text[:8000] + "... [truncated]"
        else:
            text = resp.text[:8000]

        logger.info(f"read_url OK: {url}, {len(text)} chars")
        return {"url": url, "content": text, "status": resp.status_code}
    except Exception as e:
        logger.error(f"read_url failed: {url}: {e}")
        return {"url": url, "error": str(e)}


async def _execute_reddit_search(query: str, subreddit: str = "", sort: str = "relevance", time_filter: str = "all", limit: int = 10) -> dict[str, Any]:
    try:
        reddit = _get_async_reddit()
        if not reddit:
            return {"error": "Reddit credentials not configured"}
        async with reddit:
            sub = await reddit.subreddit(subreddit if subreddit else "all")
            posts = []
            async for post in sub.search(query, sort=sort, time_filter=time_filter, limit=limit):
                posts.append({
                    "title": post.title,
                    "subreddit": str(post.subreddit),
                    "score": post.score,
                    "num_comments": post.num_comments,
                    "url": f"https://reddit.com{post.permalink}",
                    "selftext": (post.selftext[:500] + "...") if len(post.selftext) > 500 else post.selftext,
                    "author": str(post.author) if post.author else "[deleted]",
                })
        logger.info(f"reddit_search OK: query='{query}', sub={subreddit or 'all'}, results={len(posts)}")
        return {"posts": posts, "count": len(posts)}
    except Exception as e:
        logger.error(f"reddit_search failed: {e}")
        return {"error": str(e)}


async def _execute_reddit_read_post(url: str, comment_limit: int = 10) -> dict[str, Any]:
    try:
        reddit = _get_async_reddit()
        if not reddit:
            return {"error": "Reddit credentials not configured"}
        async with reddit:
            submission = await reddit.submission(url=url)
            await submission.comments.replace_more(limit=0)
            comments = []
            for c in submission.comments[:comment_limit]:
                comments.append({
                    "author": str(c.author) if c.author else "[deleted]",
                    "body": (c.body[:400] + "...") if len(c.body) > 400 else c.body,
                    "score": c.score,
                })
        logger.info(f"reddit_read_post OK: {url}, {len(comments)} comments")
        return {
            "title": submission.title,
            "subreddit": str(submission.subreddit),
            "selftext": submission.selftext,
            "score": submission.score,
            "num_comments": submission.num_comments,
            "comments": comments,
        }
    except Exception as e:
        logger.error(f"reddit_read_post failed: {e}")
        return {"error": str(e)}


async def _execute_reddit_subreddit(subreddit: str, sort: str = "hot", time_filter: str = "day", limit: int = 10) -> dict[str, Any]:
    try:
        reddit = _get_async_reddit()
        if not reddit:
            return {"error": "Reddit credentials not configured"}
        async with reddit:
            sub = await reddit.subreddit(subreddit)
            if sort == "top":
                posts_iter = sub.top(time_filter=time_filter, limit=limit)
            elif sort == "new":
                posts_iter = sub.new(limit=limit)
            elif sort == "rising":
                posts_iter = sub.rising(limit=limit)
            else:
                posts_iter = sub.hot(limit=limit)
            posts = []
            async for post in posts_iter:
                posts.append({
                    "title": post.title,
                    "score": post.score,
                    "num_comments": post.num_comments,
                    "url": f"https://reddit.com{post.permalink}",
                    "selftext": (post.selftext[:300] + "...") if len(post.selftext) > 300 else post.selftext,
                })
        logger.info(f"reddit_subreddit OK: r/{subreddit} ({sort}), {len(posts)} posts")
        return {"subreddit": subreddit, "sort": sort, "posts": posts}
    except Exception as e:
        logger.error(f"reddit_subreddit failed: {e}")
        return {"error": str(e)}


async def _execute_delegate_to_agent(agent_name: str, task: str, session_id: str = "") -> dict[str, Any]:
    """Run a sub-agent with its own tool loop and return its output."""
    from core.agents.registry import agent_registry

    try:
        agent_def = agent_registry.get(agent_name)
    except KeyError:
        return {"error": f"Agent '{agent_name}' not found"}

    api_key = os.environ.get("GEMINI_API_KEY", "") or os.environ.get("GOOGLE_API_KEY", "") or settings.google_api_key
    if not api_key:
        return {"error": "No API key configured"}

    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)
    sub_model = agent_def.model or settings.default_model
    tool_declarations = _build_tool_declarations()

    contents = [types.Content(role="user", parts=[types.Part.from_text(text=task)])]

    config = types.GenerateContentConfig(
        system_instruction=agent_def.system_prompt,
        tools=[tool_declarations],
        tool_config=types.ToolConfig(
            function_calling_config=types.FunctionCallingConfig(mode="AUTO")
        ),
    )

    logger.info(f"delegate_to_agent: running '{agent_name}' on task: {task[:100]}")

    response = client.models.generate_content(model=sub_model, contents=contents, config=config)

    # Sub-agent tool loop (up to 5 rounds)
    sub_tool_count = 0
    sub_round = 0
    for _ in range(5):
        if not response.candidates or not response.candidates[0].content.parts:
            break
        function_calls = [p for p in response.candidates[0].content.parts if p.function_call]
        if not function_calls:
            break

        sub_round += 1
        sub_tool_count += len(function_calls)
        tool_names = [fc.function_call.name for fc in function_calls]

        # Update live activity so the UI shows the sub-agent's tools blinking
        if session_id:
            _live_activity[session_id] = {
                "tool_calls": sub_tool_count,
                "tool_rounds": sub_round,
                "current_tools": tool_names,
                "status": "running",
                "delegated_agent": agent_name,
            }

        contents.append(response.candidates[0].content)

        fn_response_parts = []
        for fc in function_calls:
            fn_name = fc.function_call.name
            fn_args = dict(fc.function_call.args) if fc.function_call.args else {}
            # Prevent infinite recursion — sub-agents can't delegate
            if fn_name == "delegate_to_agent":
                result = {"error": "Sub-agents cannot delegate to other agents"}
            else:
                result = await _dispatch_tool(fn_name, fn_args)
            fn_response_parts.append(types.Part.from_function_response(name=fn_name, response=result))

        contents.append(types.Content(role="user", parts=fn_response_parts))
        response = client.models.generate_content(model=sub_model, contents=contents, config=config)

    reply = response.text or ""
    logger.info(f"delegate_to_agent: '{agent_name}' completed, {len(reply)} chars")

    return {"agent": agent_name, "task": task, "response": reply}


def _get_async_reddit():
    """Get Async PRAW Reddit instance."""
    client_id = os.environ.get("REDDIT_CLIENT_ID", "") or settings.reddit_client_id
    client_secret = os.environ.get("REDDIT_CLIENT_SECRET", "") or settings.reddit_client_secret
    if not client_id or not client_secret:
        return None
    import asyncpraw
    return asyncpraw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent="ai-agent-platform:v1.0",
    )


# ─── Tool dispatcher ─────────────────────────────────────────────────

TOOL_EXECUTORS = {
    "tavily_search": lambda args: _execute_tavily(
        query=args.get("query", ""),
        max_results=int(args.get("max_results", 5)),
        topic=args.get("topic", "general"),
    ),
    "exa_search": lambda args: _execute_exa(
        query=args.get("query", ""),
        num_results=int(args.get("num_results", 5)),
        category=args.get("category", ""),
    ),
    "calculator": lambda args: _execute_calculator(args.get("expression", "")),
    "get_current_datetime": lambda args: _execute_get_datetime(
        timezone=args.get("timezone", "UTC"),
        fmt=args.get("format", "full"),
    ),
    "read_url": lambda args: _execute_read_url(args.get("url", "")),
}


async def _dispatch_tool(fn_name: str, fn_args: dict[str, Any], session_id: str = "") -> dict[str, Any]:
    """Execute a tool by name. Returns result dict."""
    import asyncio
    import inspect

    # delegate_to_agent needs session_id for live activity updates
    if fn_name == "delegate_to_agent":
        return await _execute_delegate_to_agent(
            agent_name=fn_args.get("agent_name", ""),
            task=fn_args.get("task", ""),
            session_id=session_id,
        )

    # Reddit tools are async
    ASYNC_EXECUTORS = {
        "reddit_search": lambda args: _execute_reddit_search(
            query=args.get("query", ""),
            subreddit=args.get("subreddit", ""),
            sort=args.get("sort", "relevance"),
            time_filter=args.get("time_filter", "all"),
            limit=int(args.get("limit", 10)),
        ),
        "reddit_read_post": lambda args: _execute_reddit_read_post(
            url=args.get("url", ""),
            comment_limit=int(args.get("comment_limit", 10)),
        ),
        "reddit_subreddit": lambda args: _execute_reddit_subreddit(
            subreddit=args.get("subreddit", ""),
            sort=args.get("sort", "hot"),
            time_filter=args.get("time_filter", "day"),
            limit=int(args.get("limit", 10)),
        ),
    }

    if fn_name in ASYNC_EXECUTORS:
        return await ASYNC_EXECUTORS[fn_name](fn_args)

    executor = TOOL_EXECUTORS.get(fn_name)
    if not executor:
        return {"error": f"Unknown tool: {fn_name}"}
    return executor(fn_args)


# ─── Chat endpoint ───────────────────────────────────────────────────

@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    api_key = os.environ.get("GEMINI_API_KEY", "") or os.environ.get("GOOGLE_API_KEY", "") or settings.google_api_key
    session_id = req.session_id or str(uuid.uuid4())

    # Resolve agent config (overrides model + system prompt)
    system_prompt = req.system or DEFAULT_SYSTEM
    model = req.model or settings.default_model
    agent_name = req.agent or ""

    if agent_name:
        from core.agents.registry import agent_registry
        try:
            agent_def = agent_registry.get(agent_name)
            system_prompt = agent_def.system_prompt
            model = agent_def.model or model
            logger.info(f"Using agent '{agent_name}' with model={model}")
        except KeyError:
            logger.warning(f"Agent '{agent_name}' not found, using defaults")

    if not api_key:
        return ChatResponse(
            reply="[Mock] No API key configured. Your message was: " + req.message,
            model="mock",
            session_id=session_id,
        )

    if session_id not in _sessions:
        _sessions[session_id] = []

    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)

    # Build tools — combine Google Search + function declarations in one Tool
    use_google_search = req.google_search
    fn_declarations = _build_tool_declarations()

    if use_google_search:
        # Combine: Google Search + custom functions in same Tool object
        tools_list = [
            types.Tool(
                google_search=types.GoogleSearch(),
                function_declarations=fn_declarations.function_declarations,
            ),
        ]
    else:
        tools_list = [fn_declarations]

    # Tool config — controls calling mode
    tool_mode = req.tool_mode.upper() if req.tool_mode else "AUTO"
    tool_config = types.ToolConfig(
        function_calling_config=types.FunctionCallingConfig(mode=tool_mode)
    )

    # Build contents from session history + new message
    contents = []
    for m in _sessions[session_id]:
        contents.append(types.Content(
            role=m["role"],
            parts=[types.Part.from_text(text=m["text"])],
        ))
    contents.append(types.Content(
        role="user",
        parts=[types.Part.from_text(text=req.message)],
    ))

    start = time.monotonic()
    tool_calls_made = []
    tool_steps: list[ToolStep] = []
    tool_rounds = 0

    try:
        config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            tools=tools_list,
            tool_config=tool_config,
        )

        response = client.models.generate_content(
            model=model, contents=contents, config=config,
        )

        # ── Tool use loop (parallel + compositional) ──
        # Each round can have multiple parallel function calls.
        # The model can chain results across rounds (compositional).
        max_rounds = max(1, min(req.research_depth, MAX_TOOL_ROUNDS))
        for round_num in range(max_rounds):
            if not response.candidates or not response.candidates[0].content.parts:
                break

            function_calls = [p for p in response.candidates[0].content.parts if p.function_call]
            if not function_calls:
                break

            tool_rounds += 1
            logger.info(f"Tool round {tool_rounds}: {len(function_calls)} parallel call(s)")

            # Update live activity for polling
            _live_activity[session_id] = {
                "tool_calls": len(tool_calls_made) + len(function_calls),
                "tool_rounds": tool_rounds,
                "current_tools": [fc.function_call.name for fc in function_calls],
                "status": "running",
            }

            # Add model's response (with function calls) to contents
            contents.append(response.candidates[0].content)

            # Track this round's calls
            round_calls: list[ToolCallInfo] = []

            # Execute ALL function calls in this round (parallel execution)
            fn_response_parts = []
            for fc in function_calls:
                fn_name = fc.function_call.name
                fn_args = dict(fc.function_call.args) if fc.function_call.args else {}

                logger.info(f"  -> {fn_name}({fn_args})")
                result = await _dispatch_tool(fn_name, fn_args, session_id=session_id)
                has_error = "error" in result

                tool_calls_made.append({
                    "tool": fn_name,
                    "args": fn_args,
                    "round": tool_rounds,
                    "result_preview": str(result)[:200],
                })

                round_calls.append(ToolCallInfo(
                    tool=fn_name,
                    args=fn_args,
                    result_preview=str(result)[:300],
                    success=not has_error,
                ))

                fn_response_parts.append(
                    types.Part.from_function_response(name=fn_name, response=result)
                )

            tool_steps.append(ToolStep(round=tool_rounds, calls=round_calls))

            # Add all function results back
            contents.append(types.Content(role="user", parts=fn_response_parts))

            # Next round — model may call more tools (compositional chaining)
            # or produce a final text response
            response = client.models.generate_content(
                model=model, contents=contents, config=config,
            )

        elapsed = (time.monotonic() - start) * 1000

        # Extract text safely — response may have mixed text + function_call parts
        try:
            reply_text = response.text or ""
        except Exception:
            # Fallback: manually extract text parts
            reply_text = ""
            if response.candidates and response.candidates[0].content.parts:
                text_parts = [p.text for p in response.candidates[0].content.parts if hasattr(p, 'text') and p.text]
                reply_text = "\n".join(text_parts)

        # Clear live activity
        _live_activity.pop(session_id, None)

        # Extract grounding metadata from Google Search
        grounding_sources = []
        search_queries = []
        if response.candidates:
            gm = getattr(response.candidates[0], "grounding_metadata", None)
            if gm:
                # Extract search queries used
                for q in getattr(gm, "web_search_queries", []) or []:
                    search_queries.append(q)
                # Extract grounding chunks (sources)
                for chunk in getattr(gm, "grounding_chunks", []) or []:
                    web = getattr(chunk, "web", None)
                    if web:
                        grounding_sources.append(GroundingSource(
                            title=getattr(web, "title", "") or "",
                            url=getattr(web, "uri", "") or "",
                        ))
                if grounding_sources:
                    logger.info(f"Google Search grounding: {len(grounding_sources)} sources, queries={search_queries}")

        # Save to session (text only)
        _sessions[session_id].append({"role": "user", "text": req.message})
        _sessions[session_id].append({"role": "model", "text": reply_text})

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
            tool_steps=[s.model_dump() for s in tool_steps],
            tool_rounds=tool_rounds,
            grounding_sources=[s.model_dump() for s in grounding_sources],
            search_queries=search_queries,
        )

    except Exception as e:
        elapsed = (time.monotonic() - start) * 1000
        _live_activity.pop(session_id, None)
        logger.error(f"Chat error: {e}", exc_info=True)
        return ChatResponse(
            reply=f"Error: {str(e)}",
            model=model,
            session_id=session_id,
            latency_ms=elapsed,
        )


# ─── Live activity polling ────────────────────────────────────────────

@router.get("/activity")
async def get_activity(session_id: str):
    """Poll current tool activity for a session."""
    activity = _live_activity.get(session_id)
    if not activity:
        return {"status": "idle", "tool_calls": 0, "tool_rounds": 0, "current_tools": []}
    return activity


# ─── Deep dive query generator ────────────────────────────────────────

class DiveRequest(BaseModel):
    headline: str
    detail: str = ""
    original_query: str = ""
    session_id: str = ""


@router.post("/dive")
async def generate_dive_query(req: DiveRequest):
    """Use Gemini to generate an optimal follow-up research query."""
    api_key = os.environ.get("GEMINI_API_KEY", "") or os.environ.get("GOOGLE_API_KEY", "") or settings.google_api_key
    if not api_key:
        return {"query": f"Tell me more about: {req.headline}"}

    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)

    # Collect prior user queries to avoid repetition
    prior_queries = []
    if req.session_id and req.session_id in _sessions:
        for m in _sessions[req.session_id]:
            if m["role"] == "user":
                prior_queries.append(m["text"][:120])
    prior_list = "\n".join(f"- {q}" for q in prior_queries[-6:]) if prior_queries else "None"

    # Single focused call — the finding detail IS the context
    prompt = f"""Read this research finding carefully, then generate ONE specific follow-up research question.

FINDING HEADLINE: {req.headline}

FINDING CONTENT:
{req.detail or req.headline}

ORIGINAL RESEARCH TOPIC: {req.original_query or 'N/A'}

PREVIOUS QUERIES (do not repeat these):
{prior_list}

INSTRUCTIONS:
1. Read the finding content word by word
2. Identify the most interesting specific detail — a name, place, substance, event, statistic, or claim
3. Generate a question that digs deeper into THAT specific detail
4. The question MUST reference specific entities from the finding (names, places, substances, dates)

EXAMPLES based on the finding above:
- If finding mentions a substance: "What are the specific health effects of [substance] and how are first responders in [location] adapting their protocols?"
- If finding mentions a person: "What is [person]'s current status and involvement in [topic]?"
- If finding mentions a statistic: "How does [statistic] compare to [related metric] over the past 5 years?"
- If finding mentions a policy: "What were the measurable outcomes of [policy] since its implementation?"

Return ONLY the question. One sentence, max 30 words. Must reference a specific entity from the finding. No quotes, no em-dashes, no sub-clauses."""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(temperature=0.5, max_output_tokens=500),
    )

    return {"query": (response.text or req.headline).strip()}


# ─── Report synthesis ─────────────────────────────────────────────────

class ReportRequest(BaseModel):
    session_id: str
    title: str = ""


@router.post("/report")
async def generate_report(req: ReportRequest):
    """Synthesize all research in the session into a single markdown report."""
    api_key = os.environ.get("GEMINI_API_KEY", "") or os.environ.get("GOOGLE_API_KEY", "") or settings.google_api_key
    if not api_key:
        return {"error": "No API key configured"}

    history = _sessions.get(req.session_id, [])
    if not history:
        return {"error": "No session history found"}

    # Collect all research outputs and conversation
    research_blocks = []
    conversation = []
    for m in history:
        conversation.append(f"**{m['role']}**: {m['text'][:500]}")
        if m["role"] == "model":
            # Try to extract structured research
            text = m["text"]
            match = None
            import re
            json_match = re.search(r'```json\s*([\s\S]*?)```', text)
            if json_match:
                try:
                    import json
                    data = json.loads(json_match.group(1))
                    if "key_findings" in data:
                        research_blocks.append(data)
                except Exception:
                    pass
            if not research_blocks or research_blocks[-1] != (data if json_match else None):
                # Include non-structured responses too
                pass

    if not research_blocks:
        return {"error": "No structured research found in this session"}

    # Build a synthesis prompt with all research data
    research_summary = ""
    all_sources = []
    for i, block in enumerate(research_blocks, 1):
        research_summary += f"\n\n--- Research Block {i}: {block.get('title', 'Untitled')} ---\n"
        research_summary += f"Summary: {block.get('summary', '')}\n"
        for f in block.get("key_findings", []):
            research_summary += f"- [{f.get('confidence', '?')}] {f.get('headline', '')}: {f.get('detail', '')[:300]}\n"
        if block.get("analysis"):
            research_summary += f"Analysis: {block['analysis'][:500]}\n"
        for s in block.get("sources", []):
            all_sources.append(s)

    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)

    prompt = f"""Synthesize the following research findings into a single comprehensive report.

Title: {req.title or 'Research Report'}

Research Data:
{research_summary}

Full conversation for context:
{chr(10).join(conversation[-20:])}

Write a professional markdown report with:

# {req.title or 'Research Report'}
**Generated:** [today's date]

## Executive Summary
2-3 paragraph overview of all findings

## Key Findings
Numbered list with full detail paragraphs for each finding, citing sources

## Analysis
Comprehensive narrative connecting all research threads

## Implications & Recommendations
What this means and suggested next steps

## Methodology
Brief note on research approach (web searches, source verification, etc.)

## Sources
Full numbered list of all sources with URLs

Make it thorough, well-structured, and ready to share. Use markdown formatting throughout."""

    response = client.models.generate_content(
        model="gemini-3.1-pro-preview",
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.3,
            max_output_tokens=8192,
        ),
    )

    return {
        "report": response.text or "",
        "research_blocks": len(research_blocks),
        "total_sources": len(all_sources),
    }


# ─── History endpoints ────────────────────────────────────────────────

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
