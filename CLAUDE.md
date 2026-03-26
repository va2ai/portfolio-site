# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Multi-agent AI platform with pluggable LLM providers, tools, and runtimes. Includes a FastAPI backend with chat UI, function calling (parallel + compositional), research agent, and web search tools (Tavily, Exa, Google Search grounding). Powered by Google Gemini.

## Commands

```bash
# Setup
python -m venv .venv
.venv\Scripts\Activate.ps1          # Windows
pip install -e ".[dev]"
cp .env.example .env                # add API keys

# Run (must be in project root with venv activated)
.venv\Scripts\python -m uvicorn apps.api.main:app --reload

# Examples (no API keys needed — use mock providers)
python -m examples.simple_chat.main
python -m examples.rag_assistant.main
```

No test runner or linter is configured yet. `ruff` and `pytest` are in dev dependencies.

## Architecture

**Layered Core + Adapter Shell** — business logic in `core/`, vendor integrations in `adapters/`, API in `apps/`.

### Protocol-based abstractions (all in `*/base.py`)

| Protocol | Location | Key methods |
|----------|----------|-------------|
| `LLMClient` | `core/llm/base.py` | `generate()`, `generate_structured()`, `stream()`, `embed()` |
| `BaseTool` | `core/tools/base.py` | `input_schema()`, `execute()` |
| `AgentRuntime` | `adapters/runtimes/base.py` | `run_task()`, `handoff()`, `stream_events()` |
| `VectorStore` | `adapters/vectorstores/base.py` | `upsert()`, `search()`, `delete()` |

### Singleton registries

- `tool_registry` (`core/tools/registry.py`) — all tools registered at startup in `apps/api/main.py` lifespan
- `agent_registry` (`core/agents/registry.py`) — agent definitions (name, system_prompt, tools, model)

### Chat endpoint (`apps/api/routes/chat.py`)

This is the largest and most complex file. It handles:
- **Gemini function calling** with parallel + compositional tool chaining
- **Tool modes:** AUTO / ANY / NONE (via `ToolConfig`)
- **Research depth:** configurable max tool rounds (1-10)
- **Google Search grounding:** combined with function declarations in same `Tool` object
- **Session history:** in-memory dict `_sessions[session_id]`, stores simple `{"role", "text"}` dicts (not SDK objects)
- **Dive endpoint** (`/api/dive`): generates AI-powered follow-up queries from research findings
- **Report endpoint** (`/api/report`): synthesizes all session research into markdown report

Tool executors are defined inline (not via the tool registry) for the function calling loop: `_execute_tavily()`, `_execute_exa()`, `_execute_calculator()`, `_execute_get_datetime()`, `_execute_read_url()`. Dispatched via `TOOL_EXECUTORS` dict.

### UI (`apps/api/routes/ui.py`)

Single-file HTML/CSS/JS served at `/`. Contains:
- Chat with markdown rendering (marked.js), message edit/delete, system prompt editor
- Structured research output parser (`tryParseResearch`) — renders JSON findings as expandable accordions
- Tool step visualization (collapsible round-by-round display)
- Grounding sources panel (collapsible, closed by default)
- Animated status messages during agent processing
- Export report modal with copy/download

### Research agent (`core/agents/builtins/research_agent.py`)

Returns structured JSON in a ```json code block with: `title`, `summary`, `key_findings[]` (headline, detail, confidence, tags), `analysis`, `sources[]`, `metadata`. The UI parses this and renders interactive findings.

## Key Conventions

- **Agent libraries stay in adapters** — never import CrewAI/LangGraph in `core/`
- **All tool calls through gateway** — `core/tools/gateway.py` handles validation, logging, timeout
- **Structured I/O** — Pydantic models for all agent/tool inputs and API responses
- **API key resolution:** `os.environ > settings (.env)` — see chat.py pattern: `os.environ.get("GEMINI_API_KEY") or settings.google_api_key`
- **Config:** `core/shared/config.py` via pydantic-settings, loads `.env`
- **Errors:** `core/shared/exceptions.py` — `LLMError`, `ToolError`, `RetrievalError`
- **Cost tracking:** `core/observability/cost_tracking.py` has per-model token pricing
- **Session history truncates to 40 messages** and stores text-only dicts (no SDK objects — those break serialization)

## Adding a New Tool

1. Create `core/tools/builtins/my_tool.py` extending `BaseTool`
2. Register in `apps/api/main.py` lifespan
3. Add Gemini `FunctionDeclaration` in `_build_tool_declarations()` in `chat.py`
4. Add executor function and entry in `TOOL_EXECUTORS` dict in `chat.py`

## Adding a New Agent

1. Create `core/agents/builtins/my_agent.py` with an `AgentDefinition`
2. Register in `apps/api/main.py` lifespan
3. Add `<option>` to `agentSelect` in `ui.py`

## Deployment

```bash
# Docker
docker compose up

# Manual
pip install -e . && uvicorn apps.api.main:app --host 0.0.0.0 --port 8000
```

Environment: `GEMINI_API_KEY`, `TAVILY_API_KEY`, `EXA_API_KEY` (optional: `PGVECTOR_CONNECTION`, `OTEL_EXPORTER_OTLP_ENDPOINT`)
