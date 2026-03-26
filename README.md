# ai-agent-platform

Multi-agent AI platform with pluggable tools, parallel function calling, and a built-in research agent. Powered by Google Gemini 3.1 Pro / Flash.

## Quick Start

```bash
python -m venv .venv
# Windows
.venv\Scripts\Activate.ps1
# Linux/Mac
source .venv/bin/activate

pip install -e ".[dev]"
cp .env.example .env  # add your API keys

# Start the server
.venv\Scripts\python -m uvicorn apps.api.main:app --reload

# Open http://localhost:8000
```

## Features

**Chat UI** at `/` with model selector, agent picker, tool mode, research depth slider, system prompt editor, message history editing, and markdown rendering.

**6 Built-in Tools**
| Tool | Description |
|------|-------------|
| `tavily_search` | AI web search (news, facts, recent events) |
| `exa_search` | Semantic neural search (papers, companies, people) |
| `calculator` | Math with sqrt, trig, log, pi, e |
| `get_current_datetime` | Current date/time in any timezone |
| `read_url` | Fetch and extract text from URLs |
| `google_search` | Native Gemini grounding with Google Search |

**Research Agent** — select "Research" in the UI for deep multi-step investigation:
- Decomposes questions into parallel sub-queries
- Searches Tavily + Exa simultaneously
- Reads full articles, cross-references, verifies claims
- Returns structured findings with confidence levels and sources
- "Research deeper" button generates AI-powered follow-up queries
- Export to markdown report

**Advanced Function Calling**
- Parallel: multiple tools in one round
- Compositional: chain tool outputs across rounds (up to 10)
- Tool modes: Auto / Force / Off
- Google Search grounding combined with custom tools

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Chat UI |
| `GET` | `/health` | Health check |
| `POST` | `/api/chat` | Chat with function calling |
| `GET` | `/api/agents` | List registered agents |
| `GET` | `/api/tools` | List registered tools |
| `POST` | `/api/search` | Direct Tavily search |
| `POST` | `/api/retrieve` | RAG retrieval |
| `POST` | `/api/dive` | Generate follow-up research query |
| `POST` | `/api/report` | Synthesize session into report |
| `GET` | `/api/history` | Get session message history |
| `POST` | `/api/history/edit` | Edit a message |
| `POST` | `/api/history/delete` | Delete a message |
| `POST` | `/api/history/clear` | Clear session |
| `GET` | `/docs` | Swagger UI |

## Architecture

```
core/                    # Domain logic (no vendor imports)
  llm/                   # LLMClient protocol + Gemini provider
  agents/                # Agent registry, executor, contracts
  tools/                 # Tool gateway, registry, builtins
  retrieval/             # RAG pipeline (chunking, search, rerank)
  memory/                # Session, working, long-term memory
  observability/         # Event bus, cost tracking
adapters/                # Vendor integrations
  runtimes/              # AgentRuntime protocol + custom runtime
  vectorstores/          # VectorStore protocol + pgvector
  telemetry/             # OpenTelemetry adapter
apps/api/                # FastAPI app + routes + UI
examples/                # Runnable demos with mock providers
```

**Key protocols** — implement these to add new providers:
- `LLMClient` (`core/llm/base.py`) — generate, stream, embed
- `BaseTool` (`core/tools/base.py`) — input_schema, execute
- `AgentRuntime` (`adapters/runtimes/base.py`) — run_task, handoff
- `VectorStore` (`adapters/vectorstores/base.py`) — upsert, search

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | Yes | Google Gemini API key |
| `TAVILY_API_KEY` | No | Tavily search (enables web search tool) |
| `EXA_API_KEY` | No | Exa semantic search |
| `PGVECTOR_CONNECTION` | No | PostgreSQL + pgvector connection string |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | No | OpenTelemetry collector endpoint |

## Docker

```bash
docker compose up
```

Starts API + PostgreSQL (pgvector) + Redis.

## Philosophy

Own the contracts, abstract the runtimes, isolate the vendors, treat agent libraries as plugins.
