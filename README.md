# ai-agent-platform

Multi-agent AI platform with pluggable tools, parallel + compositional function calling, agent delegation, and a built-in research system. Powered by Google Gemini.

**Live:** https://portfolio-agent-301313738047.us-central1.run.app

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

**Chat UI** at `/` with model selector, agent picker, tool mode, research depth slider, system prompt editor, message history editing, markdown rendering, and live tool activity display.

**2 Agents**

| Agent | Description |
|-------|-------------|
| **Research** | Deep multi-step web researcher. Decomposes questions into parallel sub-queries across Tavily + Exa, reads full articles, cross-references, and returns structured findings with confidence levels. Can delegate to Reddit agent for community perspectives. |
| **Reddit** | Community researcher using async PRAW. Mines Reddit discussions, opinions, and real experiences across subreddits. Cross-references with Tavily/Exa for fact-checking. Can delegate back to Research agent for deeper verification. |

**9 Built-in Tools**

| Tool | Description |
|------|-------------|
| `tavily_search` | AI web search (news, facts, recent events) |
| `exa_search` | Semantic neural search (papers, companies, people) |
| `reddit_search` | Search Reddit across subreddits with sort/time filters |
| `reddit_read_post` | Fetch full post + top comments from Reddit |
| `reddit_subreddit` | Browse subreddit posts (hot/new/top/rising) |
| `calculator` | Math with sqrt, trig, log, pi, e |
| `get_current_datetime` | Current date/time in any timezone |
| `read_url` | Fetch and extract main text from URLs |
| `google_search` | Native Gemini grounding with Google Search |

**Research System**
- Structured JSON output with title, summary, key_findings (headline, detail, confidence, tags), analysis, and sources
- Interactive findings rendered as expandable accordions in the UI
- "Research deeper" button generates AI-powered follow-up queries
- Export session to markdown report
- Configurable research depth (1-10 tool rounds)

**Agent Delegation** — agents can hand off to each other via `delegate_to_agent`. Research agent delegates to Reddit for community perspectives; Reddit agent delegates to Research for fact verification.

**Advanced Function Calling**
- Parallel: multiple tools in one round
- Compositional: chain tool outputs across rounds (up to 10)
- Tool modes: Auto / Force / Off
- Google Search grounding combined with custom tools

**Live Activity Polling** — real-time tool execution status displayed as animated chips in the UI via `/api/activity`.

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
| `GET` | `/api/activity` | Live tool activity polling |
| `POST` | `/api/dive` | Generate follow-up research queries |
| `POST` | `/api/report` | Synthesize session into markdown report |
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
    builtins/            # research_agent, reddit_agent
  tools/                 # Tool gateway, registry, builtins
    builtins/            # tavily, exa, reddit, calculator, etc.
  retrieval/             # RAG pipeline (chunking, search, rerank)
  memory/                # Session, working, long-term memory
  observability/         # Event bus, cost tracking
adapters/                # Vendor integrations
  runtimes/              # AgentRuntime protocol + custom runtime
  vectorstores/          # VectorStore protocol + pgvector
  telemetry/             # OpenTelemetry adapter
apps/api/                # FastAPI app + routes + UI
  static/                # Frontend (index.html, style.css, app.js)
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
| `GEMINI_API_KEY` or `GOOGLE_API_KEY` | Yes | Google Gemini API key |
| `TAVILY_API_KEY` | No | Tavily search (enables web search tool) |
| `EXA_API_KEY` | No | Exa semantic search |
| `REDDIT_CLIENT_ID` | No | Reddit API client ID (enables Reddit tools) |
| `REDDIT_CLIENT_SECRET` | No | Reddit API client secret |
| `REDDIT_USER_AGENT` | No | Reddit API user agent string |
| `PGVECTOR_CONNECTION` | No | PostgreSQL + pgvector connection string |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | No | OpenTelemetry collector endpoint |

## Docker

```bash
docker compose up
```

Starts API + PostgreSQL (pgvector) + Redis.

## Philosophy

Own the contracts, abstract the runtimes, isolate the vendors, treat agent libraries as plugins.
