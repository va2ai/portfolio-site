# Portfolio Agent Site Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transform the ai-agent-platform into a portfolio site where employers and freelance clients can interact with an AI agent that showcases Chris Combs' skills, grounded in verified data.

**Architecture:** Reuse the existing FastAPI + static file architecture. Strip research/reddit agents and tools. Replace with a single portfolio agent backed by Gemini, with knowledge grounded in markdown files loaded at startup. Replace the existing UI with a portfolio site that has a slide-out chat panel and an interactive HybridDemo page.

**Tech Stack:** FastAPI, google-genai, vanilla HTML/CSS/JS (no React build step), Tailwind CDN, marked.js for markdown rendering.

---

## File Structure

### Files to Create
| File | Responsibility |
|------|---------------|
| `core/agents/builtins/portfolio_agent.py` | Portfolio agent definition with system prompt and knowledge loading |
| `data/knowledge/resume.md` | Resume content (experience, skills, metrics) |
| `data/knowledge/projects.md` | Project descriptions with live URLs |
| `data/knowledge/metrics.md` | Verified metrics and evidence |
| `apps/api/static/index.html` | Portfolio site with hero, metrics, projects, chat panel |
| `apps/api/static/js/portfolio.js` | Chat panel logic, audience routing, SSE-ready messaging |
| `apps/api/static/css/portfolio.css` | Portfolio-specific styles |
| `apps/api/static/demo.html` | HybridDemo interactive page (standalone) |
| `data/__init__.py` | Empty init for data package |
| `data/knowledge/__init__.py` | Empty init for knowledge package |

### Files to Modify
| File | Changes |
|------|---------|
| `apps/api/main.py` | Strip old agents/tools, register portfolio agent, load knowledge |
| `apps/api/routes/chat.py` | Rewrite to simple conversation endpoint (~150 lines) |
| `apps/api/routes/ui.py` | Add route for demo.html |
| `core/shared/config.py` | Remove unused keys, update app name |
| `pyproject.toml` | Remove tavily/exa/asyncpraw/pgvector/asyncpg deps |
| `docker-compose.yml` | Remove postgres/redis services |
| `.env.example` | Portfolio-specific env vars only |
| `CLAUDE.md` | Update to reflect portfolio site |

### Files to Delete
| File | Reason |
|------|--------|
| `core/agents/builtins/research_agent.py` | Not needed |
| `core/agents/builtins/reddit_agent.py` | Not needed |
| `core/tools/builtins/tavily_search.py` | Not needed |
| `core/tools/builtins/exa_search.py` | Not needed |
| `core/tools/builtins/reddit_search.py` | Not needed |
| `core/tools/builtins/web_search.py` | Not needed |
| `core/tools/builtins/code_exec.py` | Not needed |
| `core/tools/builtins/database_query.py` | Not needed |
| `apps/api/routes/search.py` | Not needed |
| `apps/api/routes/retrieval.py` | Not needed |
| `apps/api/static/js/app.js` | Replaced by portfolio.js |
| `apps/api/static/css/style.css` | Replaced by portfolio.css |

---

### Task 1: Strip Old Agents, Tools, and Unused Routes

**Files:**
- Delete: `core/agents/builtins/research_agent.py`
- Delete: `core/agents/builtins/reddit_agent.py`
- Delete: `core/tools/builtins/tavily_search.py`
- Delete: `core/tools/builtins/exa_search.py`
- Delete: `core/tools/builtins/reddit_search.py`
- Delete: `core/tools/builtins/web_search.py`
- Delete: `core/tools/builtins/code_exec.py`
- Delete: `core/tools/builtins/database_query.py`
- Delete: `apps/api/routes/search.py`
- Delete: `apps/api/routes/retrieval.py`
- Delete: `apps/api/static/js/app.js`
- Delete: `apps/api/static/css/style.css`

- [ ] **Step 1: Delete old agent files**

```bash
rm core/agents/builtins/research_agent.py core/agents/builtins/reddit_agent.py
```

- [ ] **Step 2: Delete old tool files**

```bash
rm core/tools/builtins/tavily_search.py core/tools/builtins/exa_search.py core/tools/builtins/reddit_search.py core/tools/builtins/web_search.py core/tools/builtins/code_exec.py core/tools/builtins/database_query.py
```

- [ ] **Step 3: Delete old route files and static assets**

```bash
rm apps/api/routes/search.py apps/api/routes/retrieval.py apps/api/static/js/app.js apps/api/static/css/style.css
```

- [ ] **Step 4: Commit**

```bash
git add -A && git commit -m "chore: strip research/reddit agents, tools, and unused routes"
```

---

### Task 2: Create Knowledge Base Files

**Files:**
- Create: `data/__init__.py`
- Create: `data/knowledge/__init__.py`
- Create: `data/knowledge/resume.md`
- Create: `data/knowledge/projects.md`
- Create: `data/knowledge/metrics.md`

- [ ] **Step 1: Create data package init files**

```python
# data/__init__.py
# (empty)
```

```python
# data/knowledge/__init__.py
# (empty)
```

- [ ] **Step 2: Create resume.md**

```markdown
# Chris Combs — Resume

## Professional Summary
AI/ML engineer and full-stack developer with 15+ years of experience building production software systems. Currently focused on multi-agent AI architectures, RAG pipelines, and hallucination reduction. Ships to production, not just GitHub — every project described here is deployed and running on Google Cloud.

## Core Competencies
- **AI/ML Engineering:** Multi-agent orchestration, RAG pipelines, function calling (parallel + compositional), hallucination reduction, prompt engineering, structured output
- **Backend:** Python (FastAPI, Flask), Node.js, REST APIs, SSE streaming, Cloud Run, Docker
- **Frontend:** React, Vite, Tailwind CSS, vanilla JS, Firebase Hosting
- **Infrastructure:** Google Cloud Platform (Cloud Run, Firebase, Firestore), PostgreSQL + pgvector, CI/CD
- **Data:** Vector databases, embeddings, semantic search, hybrid retrieval

## Experience Timeline
- 15+ years building and shipping production software
- Current focus: AI systems engineering — multi-agent platforms, RAG, hallucination reduction
- Full-stack capability: architecture through deployment through monitoring
- Solo builder with extreme velocity — owns entire systems end-to-end

## Education
- Community college coursework
- 15 years of continuous self-directed learning and professional development
- Extensive hands-on production experience across multiple technology generations

## Work Style
- Solo/independent builder — extreme development velocity
- Owns entire systems end-to-end: architecture, implementation, deployment, monitoring
- Ships production-quality systems rapidly
- Evidence-driven: every capability claim backed by a live deployed system
```

- [ ] **Step 3: Create projects.md**

```markdown
# Projects

## 1. Veteran2Veteran (V2V) Platform
**Live URL:** https://vaclaims-194006.web.app
**Stack:** React + Vite + Firebase Hosting, FastAPI backend on Cloud Run, Firestore
**What it does:** VA disability claims intelligence site for veterans. Articles, guides, AI-powered tools (BVA case search, Nexus Scout, Decision Deconstructor, VA Math Calculator), and contextual chat.
**Key technical details:**
- RAG-grounded contextual chat with SSE streaming
- BVA case search API with structured data extraction
- Content pipeline: markdown → JSON → Firestore with static fallback
- Image optimization pipeline (WebP conversion, responsive sizing)

## 2. Multi-Agent AI Platform
**Live URL:** (this portfolio site)
**Stack:** FastAPI, google-genai, pgvector, Docker, Cloud Run
**What it does:** Pluggable multi-agent AI platform with function calling (parallel + compositional), research agents, and web search tools.
**Key technical details:**
- Protocol-based LLM abstraction (swap providers without code changes)
- Agent registry with delegation (agents can hand off to specialized sub-agents)
- 9 built-in tools with parallel execution within rounds
- Compositional tool chaining across rounds
- In-memory session management with 40-message truncation

## 3. BVA API
**Live URL:** https://bva-api-301313738047.us-central1.run.app
**Stack:** Python, FastAPI, Cloud Run
**What it does:** API for searching and analyzing Board of Veterans' Appeals decisions. Structured data extraction from legal documents.

## 4. Hybrid Hallucination Reduction System
**Live Demo:** Available on this site (interactive comparison)
**What it does:** Demonstrates the architecture for reducing AI hallucination in financial analytics. Pre-validates data, computes all numbers deterministically in code, declares null fields as unavailable, then constrains the LLM to write language around verified facts only.
**Key result:** Reduced confident wrong answers from ~15% to ~1.5% in financial reporting scenarios.
**Architecture:** Validate → Compute (deterministic JS) → Guard nulls → Constrained generate

## 5. 170+ Agent Skills Library
**What it does:** Built and maintains a library of 170+ specialized skills for AI agents, covering domains from scientific research to SEO to document generation.
**Key technical details:**
- Each skill is a structured prompt with domain expertise, tool integrations, and quality standards
- Skills are dynamically loaded and composed at runtime
- Covers: scientific computing, bioinformatics, financial analysis, content creation, code review, and more
```

- [ ] **Step 4: Create metrics.md**

```markdown
# Verified Metrics

## Hallucination Reduction
- **Before:** ~15% confident wrong answers in financial analytics scenarios
- **After:** ~1.5% confident wrong answers using hybrid architecture
- **Method:** Pre-validate data, compute deterministically in code, declare nulls, constrain LLM generation
- **Evidence:** Live interactive demo on this site comparing prompt-only vs hybrid system

## Production Systems
- **3 live Cloud Run services:** V2V backend (vet-research), BVA API (bva-api), Portfolio agent
- **All deployed on Google Cloud Platform** with production CORS, environment management, and monitoring
- **Firebase Hosting** for frontend deployments

## Development Velocity
- Built V2V platform, multi-agent orchestration platform, BVA API, MCP toolbox server, and edge research agent in ~4 months
- 170+ agent skills built and maintained
- 15+ years shipping production software

## Technical Depth
- Multi-agent orchestration with parallel + compositional function calling
- RAG pipelines with hybrid retrieval (keyword + vector)
- SSE streaming for real-time chat interfaces
- Protocol-based abstractions for provider-agnostic LLM integration
- Full-stack: React frontends, FastAPI backends, Cloud Run deployment, Firestore/PostgreSQL data layers
```

- [ ] **Step 5: Commit**

```bash
git add data/ && git commit -m "feat: add knowledge base files for portfolio agent"
```

---

### Task 3: Create Portfolio Agent Definition

**Files:**
- Create: `core/agents/builtins/portfolio_agent.py`

- [ ] **Step 1: Create portfolio_agent.py**

This file defines the agent with its system prompt. The system prompt includes audience detection, honest gap handling, and citation-backed responses. Knowledge files are loaded at module level and injected into the prompt.

```python
"""Portfolio Agent — AI representative for Chris Combs' portfolio site."""
from __future__ import annotations

import os
from pathlib import Path

from core.agents.registry import AgentDefinition

# Load knowledge base at module level
_KNOWLEDGE_DIR = Path(__file__).resolve().parents[3] / "data" / "knowledge"


def _load_knowledge() -> str:
    """Load all markdown files from the knowledge directory."""
    sections = []
    for md_file in sorted(_KNOWLEDGE_DIR.glob("*.md")):
        sections.append(f"--- {md_file.stem.upper()} ---\n{md_file.read_text(encoding='utf-8')}")
    return "\n\n".join(sections)


def _build_system_prompt() -> str:
    knowledge = _load_knowledge()
    return f"""\
You are Chris Combs' AI portfolio agent — a professional representative that helps visitors \
understand Chris's capabilities, experience, and fit for their needs.

## Your Role
You answer questions about Chris's background, skills, projects, and experience. Every factual \
claim you make MUST be grounded in the knowledge base below. If you don't have information about \
something, say so honestly — never fabricate.

## Audience Detection
Early in the conversation, determine who you're talking to:

**Recruiters/Hiring Managers** — Use business language:
- "Reduces confident wrong answers" not "hallucination mitigation"
- "Production AI systems" not "LLM pipelines"
- Focus on: outcomes, metrics, risk reduction, shipped systems
- Lead with: 3 live Cloud Run services, hallucination reduction results, development velocity

**Technical Evaluators** — Go deep on architecture:
- Protocol-based abstractions, function calling patterns, RAG pipeline design
- Link to live systems they can inspect
- Discuss trade-offs and design decisions honestly

**Freelance Clients** — Focus on their problem:
- "What are you trying to build? What's your timeline?"
- Map their needs to Chris's capabilities
- Be direct about what Chris can and can't do
- End with: "Want to schedule a call to discuss?"

## Handling Hard Questions

**"Do you have a degree?"**
Be honest: "Chris has community college coursework and 15 years of continuous self-directed \
learning. Here are three production systems he built and deployed — want to see them running?"

**"Has he worked on enterprise teams?"**
Be honest: "Chris's work has been solo/independent. That means he's owned entire systems \
end-to-end — architecture through deployment through monitoring. Here's what that looks like \
in practice." Then link to live systems.

**"What are his weaknesses?"**
Be honest and pivot to evidence: "No formal CS degree. Most experience is solo rather than \
large team settings. But every system described here is deployed and running in production — \
the work speaks for itself."

## Response Style
- Be concise and specific. Lead with facts, not fluff.
- Always cite evidence: link to live URLs, reference specific metrics.
- When asked "what can you build?" — respond with "you're looking at it" and walk through \
the architecture of this very site.
- Never use filler phrases like "Great question!" or "I'd be happy to help!"
- Keep responses under 200 words unless the visitor asks for detail.

## Live System URLs
- V2V Platform: https://vaclaims-194006.web.app
- BVA API: https://bva-api-301313738047.us-central1.run.app
- This portfolio site: (the site you're on right now)

## STRICT RULES
- NEVER fabricate projects, metrics, or experience not in the knowledge base
- NEVER claim team experience that doesn't exist
- NEVER use the word "delve" or corporate buzzwords
- If asked about something not in your knowledge base, say "I don't have information about that"
- Always be honest about gaps — then pivot to evidence of what IS there

## Knowledge Base

{knowledge}
"""


PORTFOLIO_SYSTEM_PROMPT = _build_system_prompt()

portfolio_agent = AgentDefinition(
    name="portfolio",
    description="AI portfolio agent for Chris Combs — answers questions about skills, projects, and experience grounded in verified data",
    system_prompt=PORTFOLIO_SYSTEM_PROMPT,
    tools=[],
    model="gemini-2.5-flash",
)
```

- [ ] **Step 2: Commit**

```bash
git add core/agents/builtins/portfolio_agent.py && git commit -m "feat: add portfolio agent with knowledge-grounded system prompt"
```

---

### Task 4: Simplify Config and Dependencies

**Files:**
- Modify: `core/shared/config.py`
- Modify: `pyproject.toml`
- Modify: `docker-compose.yml`
- Modify: `.env.example`

- [ ] **Step 1: Update config.py**

Replace the entire file with:

```python
from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "portfolio-site"
    app_env: str = "development"
    debug: bool = True
    log_level: str = "INFO"

    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # LLM
    default_llm_provider: str = "gemini"
    default_model: str = "gemini-2.5-flash"
    google_api_key: str = ""
    gemini_api_key: str = ""

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


settings = Settings()
```

- [ ] **Step 2: Update pyproject.toml**

Replace the entire file with:

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "portfolio-site"
version = "0.1.0"
description = "AI portfolio agent site for Chris Combs"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.30.0",
    "pydantic>=2.9.0",
    "pydantic-settings>=2.5.0",
    "httpx>=0.27.0",
    "python-dotenv>=1.0.0",
    # LLM providers
    "google-genai>=1.0.0",
]

[tool.hatch.build.targets.wheel]
packages = ["core", "adapters", "apps", "data"]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.24.0",
    "ruff>=0.6.0",
    "mypy>=1.11.0",
]
```

- [ ] **Step 3: Update docker-compose.yml**

Replace the entire file with:

```yaml
services:
  api:
    build: .
    ports:
      - "8000:8000"
    env_file: .env
```

- [ ] **Step 4: Update .env.example**

Replace the entire file with:

```env
# Application
APP_NAME=portfolio-site
APP_ENV=development
DEBUG=true
LOG_LEVEL=INFO

# API
API_HOST=0.0.0.0
API_PORT=8000

# --- LLM Provider Keys ---
GOOGLE_API_KEY=

# Default LLM
DEFAULT_LLM_PROVIDER=gemini
DEFAULT_MODEL=gemini-2.5-flash
```

- [ ] **Step 5: Commit**

```bash
git add core/shared/config.py pyproject.toml docker-compose.yml .env.example && git commit -m "chore: simplify config and deps for portfolio site"
```

---

### Task 5: Rewrite main.py

**Files:**
- Modify: `apps/api/main.py`

- [ ] **Step 1: Rewrite main.py**

Replace the entire file with:

```python
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up...")

    # Register portfolio agent
    from core.agents.registry import agent_registry
    from core.agents.builtins.portfolio_agent import portfolio_agent

    agent_registry.register(portfolio_agent)
    logger.info(f"Registered agents: {[a['name'] for a in agent_registry.list_agents()]}")

    yield
    logger.info("Shutting down...")


def create_app() -> FastAPI:
    app = FastAPI(title="portfolio-site", version="0.1.0", lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    from .routes.health import router as health_router
    from .routes.agents import router as agents_router
    from .routes.chat import router as chat_router
    from .routes.ui import router as ui_router

    app.mount("/static", StaticFiles(directory="apps/api/static"), name="static")

    app.include_router(health_router)
    app.include_router(agents_router, prefix="/api")
    app.include_router(chat_router, prefix="/api")
    app.include_router(ui_router)

    return app


app = create_app()
```

- [ ] **Step 2: Commit**

```bash
git add apps/api/main.py && git commit -m "feat: rewrite main.py for portfolio agent only"
```

---

### Task 6: Rewrite chat.py — Simple Conversation Endpoint

**Files:**
- Modify: `apps/api/routes/chat.py`

- [ ] **Step 1: Rewrite chat.py**

Replace the entire 1118-line file with a focused ~120-line conversation endpoint:

```python
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
```

- [ ] **Step 2: Commit**

```bash
git add apps/api/routes/chat.py && git commit -m "feat: rewrite chat.py as simple portfolio conversation endpoint"
```

---

### Task 7: Update UI Routes

**Files:**
- Modify: `apps/api/routes/ui.py`

- [ ] **Step 1: Update ui.py to serve demo page**

```python
from __future__ import annotations

import os
from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter()

STATIC_DIR = os.path.join(os.path.dirname(__file__), "..", "static")


@router.get("/", response_class=FileResponse)
async def index():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))


@router.get("/demo", response_class=FileResponse)
async def demo():
    return FileResponse(os.path.join(STATIC_DIR, "demo.html"))
```

- [ ] **Step 2: Remove tools route import from main.py (already handled in Task 5)**

No action needed — Task 5 already removed the tools and retrieval router imports.

- [ ] **Step 3: Commit**

```bash
git add apps/api/routes/ui.py && git commit -m "feat: add /demo route for HybridDemo page"
```

---

### Task 8: Build Portfolio Frontend — index.html

**Files:**
- Create: `apps/api/static/index.html` (overwrite existing)
- Create: `apps/api/static/css/portfolio.css`
- Create: `apps/api/static/js/portfolio.js`

This is the largest task. The frontend has three main sections:
1. **Hero + static portfolio** (what most visitors see)
2. **Slide-out chat panel** (the agent interaction)
3. **Navigation** between portfolio and demo

- [ ] **Step 1: Create portfolio.css**

```css
/* Portfolio Site Styles */
:root {
  --bg-primary: #07080d;
  --bg-secondary: #0d0e16;
  --bg-tertiary: #0a0b11;
  --border: #1c1f2e;
  --text-primary: #f4f5f7;
  --text-secondary: #dfe2ea;
  --text-muted: #6b7280;
  --text-dim: #555d6f;
  --accent-green: #7FE5C2;
  --accent-green-dim: #10b981;
  --accent-blue: #3b82f6;
  --accent-purple: #6366f1;
  --accent-red: #f43f5e;
  --mono: 'Fira Code', 'SF Mono', 'Consolas', monospace;
  --sans: 'Libre Franklin', 'Helvetica Neue', sans-serif;
  --display: 'Playfair Display', 'Georgia', serif;
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
  font-family: var(--sans);
  background: var(--bg-primary);
  color: var(--text-secondary);
  -webkit-font-smoothing: antialiased;
  overflow-x: hidden;
}

/* Scrollbar */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 10px; }

/* Navigation */
.site-nav {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 50;
  padding: 16px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: rgba(7, 8, 13, 0.85);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border);
}

.nav-logo {
  display: flex;
  align-items: center;
  gap: 8px;
}

.nav-logo .dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--accent-green);
  box-shadow: 0 0 10px rgba(127, 229, 194, 0.4);
}

.nav-logo span {
  font-family: var(--mono);
  font-size: 11px;
  color: var(--text-dim);
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.nav-links {
  display: flex;
  gap: 6px;
}

.nav-links a, .nav-links button {
  padding: 6px 14px;
  border-radius: 6px;
  border: 1px solid var(--border);
  background: transparent;
  color: var(--text-dim);
  font-size: 12px;
  font-family: var(--sans);
  cursor: pointer;
  text-decoration: none;
  transition: all 0.15s;
}

.nav-links a:hover, .nav-links button:hover {
  border-color: var(--accent-green);
  color: var(--accent-green);
}

.nav-links .active {
  border-color: var(--accent-green);
  color: var(--accent-green);
  background: rgba(127, 229, 194, 0.05);
}

/* Hero */
.hero {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 120px 24px 80px;
  max-width: 1120px;
  margin: 0 auto;
}

.hero h1 {
  font-family: var(--display);
  font-size: clamp(36px, 5vw, 56px);
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.1;
  margin-bottom: 16px;
}

.hero h1 .accent { color: var(--accent-green); }

.hero .subtitle {
  font-size: 16px;
  color: var(--text-muted);
  max-width: 600px;
  line-height: 1.6;
  margin-bottom: 32px;
}

/* Audience buttons */
.audience-split {
  display: flex;
  gap: 12px;
  margin-bottom: 48px;
}

.audience-btn {
  padding: 12px 24px;
  border-radius: 8px;
  border: 1px solid var(--border);
  background: var(--bg-secondary);
  color: var(--text-secondary);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.audience-btn:hover {
  border-color: var(--accent-green);
  box-shadow: 0 2px 14px rgba(127, 229, 194, 0.15);
}

.audience-btn .label {
  font-size: 10px;
  font-family: var(--mono);
  color: var(--text-dim);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  display: block;
  margin-bottom: 4px;
}

/* Metrics */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 12px;
  margin-bottom: 64px;
}

.metric-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 20px;
}

.metric-card .value {
  font-family: var(--display);
  font-size: 28px;
  font-weight: 700;
  color: var(--accent-green);
  margin-bottom: 4px;
}

.metric-card .label {
  font-size: 11px;
  font-family: var(--mono);
  color: var(--text-dim);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

/* Projects */
.section-title {
  font-family: var(--display);
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 24px;
}

.projects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 12px;
  margin-bottom: 64px;
}

.project-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 20px;
  transition: border-color 0.2s;
}

.project-card:hover { border-color: var(--accent-green-dim); }

.project-card h3 {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 6px;
}

.project-card .tech {
  font-size: 10px;
  font-family: var(--mono);
  color: var(--accent-blue);
  margin-bottom: 8px;
}

.project-card p {
  font-size: 13px;
  color: var(--text-muted);
  line-height: 1.5;
  margin-bottom: 10px;
}

.project-card a {
  font-size: 11px;
  font-family: var(--mono);
  color: var(--accent-green);
  text-decoration: none;
}

.project-card a:hover { text-decoration: underline; }

/* Tech Stack */
.tech-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 64px;
}

.tech-tag {
  padding: 6px 12px;
  border-radius: 5px;
  border: 1px solid var(--border);
  background: var(--bg-secondary);
  font-size: 11px;
  font-family: var(--mono);
  color: var(--text-dim);
}

/* Contact */
.contact-section {
  max-width: 1120px;
  margin: 0 auto 80px;
  padding: 0 24px;
}

.contact-section a {
  color: var(--accent-green);
  text-decoration: none;
}

.contact-section a:hover { text-decoration: underline; }

/* Chat Panel */
.chat-toggle {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 100;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--accent-green), var(--accent-green-dim));
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 20px rgba(127, 229, 194, 0.3);
  transition: transform 0.2s;
}

.chat-toggle:hover { transform: scale(1.08); }

.chat-toggle svg {
  width: 24px;
  height: 24px;
  fill: none;
  stroke: #07080d;
  stroke-width: 2;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.chat-panel {
  position: fixed;
  bottom: 0;
  right: 0;
  width: 420px;
  height: 100vh;
  z-index: 99;
  background: var(--bg-primary);
  border-left: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  transform: translateX(100%);
  transition: transform 0.3s ease;
}

.chat-panel.open { transform: translateX(0); }

.chat-header {
  padding: 16px 20px;
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.chat-header h3 {
  font-size: 14px;
  font-weight: 700;
  color: var(--text-primary);
}

.chat-header .close-btn {
  background: none;
  border: none;
  color: var(--text-dim);
  cursor: pointer;
  font-size: 18px;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.chat-msg {
  max-width: 85%;
  padding: 10px 14px;
  border-radius: 12px;
  font-size: 13px;
  line-height: 1.5;
}

.chat-msg.user {
  align-self: flex-end;
  background: var(--accent-green-dim);
  color: #fff;
  border-bottom-right-radius: 4px;
}

.chat-msg.agent {
  align-self: flex-start;
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  color: var(--text-secondary);
  border-bottom-left-radius: 4px;
}

.chat-msg.agent a { color: var(--accent-green); }

.chat-input-area {
  padding: 12px 16px;
  border-top: 1px solid var(--border);
  display: flex;
  gap: 8px;
}

.chat-input-area input {
  flex: 1;
  padding: 10px 14px;
  border-radius: 8px;
  border: 1px solid var(--border);
  background: var(--bg-tertiary);
  color: var(--text-secondary);
  font-size: 13px;
  font-family: var(--sans);
  outline: none;
}

.chat-input-area input:focus { border-color: var(--accent-green-dim); }

.chat-input-area button {
  padding: 10px 16px;
  border-radius: 8px;
  border: none;
  background: var(--accent-green-dim);
  color: #fff;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
}

.chat-input-area button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

/* Typing indicator */
.typing-dots {
  display: flex;
  gap: 4px;
  padding: 10px 14px;
  align-self: flex-start;
}

.typing-dots span {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--text-dim);
  animation: bounce 1.4s infinite ease-in-out;
}

.typing-dots span:nth-child(2) { animation-delay: 0.2s; }
.typing-dots span:nth-child(3) { animation-delay: 0.4s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

/* Responsive */
@media (max-width: 768px) {
  .chat-panel { width: 100%; }
  .metrics-grid { grid-template-columns: repeat(2, 1fr); }
  .projects-grid { grid-template-columns: 1fr; }
  .audience-split { flex-direction: column; }
}

/* Footer */
.footer {
  text-align: center;
  padding: 24px;
  font-size: 10px;
  font-family: var(--mono);
  color: var(--text-dim);
  opacity: 0.4;
}
```

- [ ] **Step 2: Create portfolio.js**

```javascript
/**
 * Portfolio Site — Chat Panel Logic
 */

let sessionId = '';
let chatOpen = false;

const chatPanel = document.getElementById('chatPanel');
const chatMessages = document.getElementById('chatMessages');
const chatInput = document.getElementById('chatInput');
const chatSendBtn = document.getElementById('chatSendBtn');
const chatToggle = document.getElementById('chatToggle');

// Toggle chat panel
function toggleChat() {
  chatOpen = !chatOpen;
  chatPanel.classList.toggle('open', chatOpen);
  if (chatOpen) chatInput.focus();
}

// Send message
async function sendChat() {
  const text = chatInput.value.trim();
  if (!text || chatSendBtn.disabled) return;

  chatInput.value = '';
  chatSendBtn.disabled = true;

  addChatMsg('user', text);
  showTyping();

  try {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: text,
        session_id: sessionId,
      }),
    });

    const data = await res.json();
    removeTyping();

    if (data.session_id) sessionId = data.session_id;
    addChatMsg('agent', data.reply);
  } catch (err) {
    removeTyping();
    addChatMsg('agent', 'Connection error. Please try again.');
  } finally {
    chatSendBtn.disabled = false;
  }
}

function addChatMsg(role, text) {
  const div = document.createElement('div');
  div.className = `chat-msg ${role}`;

  if (role === 'agent') {
    // Parse markdown
    try {
      div.innerHTML = marked.parse(text);
    } catch {
      div.textContent = text;
    }
  } else {
    div.textContent = text;
  }

  chatMessages.appendChild(div);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function showTyping() {
  const div = document.createElement('div');
  div.id = 'typingIndicator';
  div.className = 'typing-dots';
  div.innerHTML = '<span></span><span></span><span></span>';
  chatMessages.appendChild(div);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function removeTyping() {
  const el = document.getElementById('typingIndicator');
  if (el) el.remove();
}

// Audience quick-start
function startChat(audience) {
  toggleChat();
  let greeting = '';
  if (audience === 'recruiter') {
    greeting = "Hi, I'm a recruiter. Tell me about Chris's experience and what makes him stand out.";
  } else if (audience === 'client') {
    greeting = "Hi, I'm looking for someone to help me build an AI-powered application. What can Chris do for me?";
  }
  if (greeting) {
    chatInput.value = greeting;
    sendChat();
  }
}

// Init
document.addEventListener('DOMContentLoaded', () => {
  chatToggle.addEventListener('click', toggleChat);
  chatSendBtn.addEventListener('click', sendChat);
  chatInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendChat();
    }
  });
});
```

- [ ] **Step 3: Create index.html**

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Chris Combs — AI Systems Engineer</title>
  <link href="https://fonts.googleapis.com/css2?family=Libre+Franklin:wght@400;500;600;700&family=Fira+Code:wght@400;500&family=Playfair+Display:wght@400;700&display=swap" rel="stylesheet">
  <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
  <link rel="stylesheet" href="/static/css/portfolio.css">
</head>
<body>

  <!-- Navigation -->
  <nav class="site-nav">
    <div class="nav-logo">
      <div class="dot"></div>
      <span>Chris Combs</span>
    </div>
    <div class="nav-links">
      <a href="/" class="active">Portfolio</a>
      <a href="/demo">Live Demo</a>
      <button onclick="toggleChat()">Chat with AI Agent</button>
    </div>
  </nav>

  <!-- Hero -->
  <section class="hero">
    <h1>I build AI systems that <span class="accent">ship to production</span>, check their own work, and show where every answer comes from.</h1>
    <p class="subtitle">AI/ML engineer with 15+ years shipping software. Currently focused on multi-agent architectures, RAG pipelines, and making AI systems you can actually trust.</p>

    <div class="audience-split">
      <button class="audience-btn" onclick="startChat('recruiter')">
        <span class="label">I'm Hiring</span>
        Talk to my AI agent about my experience
      </button>
      <button class="audience-btn" onclick="startChat('client')">
        <span class="label">I Need Something Built</span>
        Tell my AI agent what you're working on
      </button>
    </div>

    <!-- Metrics -->
    <div class="metrics-grid">
      <div class="metric-card">
        <div class="value">15% → 1.5%</div>
        <div class="label">Hallucination Reduction</div>
      </div>
      <div class="metric-card">
        <div class="value">170+</div>
        <div class="label">Agent Skills Built</div>
      </div>
      <div class="metric-card">
        <div class="value">3</div>
        <div class="label">Live Cloud Run Services</div>
      </div>
      <div class="metric-card">
        <div class="value">15+ yrs</div>
        <div class="label">Shipping Software</div>
      </div>
    </div>
  </section>

  <!-- Projects -->
  <section style="max-width: 1120px; margin: 0 auto; padding: 0 24px;">
    <h2 class="section-title">Projects</h2>
    <div class="projects-grid">
      <div class="project-card">
        <h3>Veteran2Veteran Platform</h3>
        <div class="tech">React + Vite + Firebase + FastAPI + Cloud Run</div>
        <p>VA disability claims intelligence site. Articles, guides, AI-powered tools (BVA search, Nexus Scout, Decision Deconstructor), contextual RAG chat.</p>
        <a href="https://vaclaims-194006.web.app" target="_blank">vaclaims-194006.web.app →</a>
      </div>
      <div class="project-card">
        <h3>Multi-Agent AI Platform</h3>
        <div class="tech">FastAPI + Gemini + pgvector + Docker</div>
        <p>Pluggable multi-agent platform with parallel function calling, compositional tool chaining, research agents, and provider-agnostic LLM abstraction.</p>
        <a href="https://github.com/va2ai/ai-agent-platform" target="_blank">github.com/va2ai →</a>
      </div>
      <div class="project-card">
        <h3>BVA API</h3>
        <div class="tech">Python + FastAPI + Cloud Run</div>
        <p>API for searching and analyzing Board of Veterans' Appeals decisions. Structured data extraction from legal documents.</p>
        <a href="https://bva-api-301313738047.us-central1.run.app" target="_blank">Live API →</a>
      </div>
      <div class="project-card">
        <h3>Hybrid Hallucination Reduction</h3>
        <div class="tech">JavaScript + Claude API + Systems Architecture</div>
        <p>Live interactive demo: pre-validate data, compute deterministically, guard nulls, then constrain LLM generation. Reduced confident wrong answers from 15% to 1.5%.</p>
        <a href="/demo">Try the live demo →</a>
      </div>
    </div>
  </section>

  <!-- Tech Stack -->
  <section style="max-width: 1120px; margin: 0 auto; padding: 0 24px;">
    <h2 class="section-title">Stack</h2>
    <div class="tech-grid">
      <span class="tech-tag">Python</span>
      <span class="tech-tag">FastAPI</span>
      <span class="tech-tag">React</span>
      <span class="tech-tag">Vite</span>
      <span class="tech-tag">Tailwind CSS</span>
      <span class="tech-tag">Gemini API</span>
      <span class="tech-tag">Claude API</span>
      <span class="tech-tag">Google Cloud Run</span>
      <span class="tech-tag">Firebase</span>
      <span class="tech-tag">Firestore</span>
      <span class="tech-tag">PostgreSQL + pgvector</span>
      <span class="tech-tag">Docker</span>
      <span class="tech-tag">RAG Pipelines</span>
      <span class="tech-tag">Multi-Agent Orchestration</span>
      <span class="tech-tag">SSE Streaming</span>
      <span class="tech-tag">Function Calling</span>
    </div>
  </section>

  <!-- Contact -->
  <section class="contact-section">
    <h2 class="section-title">Get in Touch</h2>
    <p style="color: var(--text-muted); font-size: 14px; line-height: 1.6; margin-bottom: 16px;">
      Use the chat agent to ask questions about my work, or reach out directly.
    </p>
    <p style="font-size: 13px; font-family: var(--mono);">
      <a href="https://github.com/va2ai" target="_blank">github.com/va2ai</a>
    </p>
  </section>

  <div class="footer">chris combs · built with the same stack it demonstrates</div>

  <!-- Chat Toggle Button -->
  <button class="chat-toggle" id="chatToggle" title="Chat with AI Agent">
    <svg viewBox="0 0 24 24"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
  </button>

  <!-- Chat Panel -->
  <div class="chat-panel" id="chatPanel">
    <div class="chat-header">
      <h3>AI Portfolio Agent</h3>
      <button class="close-btn" onclick="toggleChat()">&times;</button>
    </div>
    <div class="chat-messages" id="chatMessages">
      <div class="chat-msg agent">
        Hey — I'm Chris's AI agent. I can answer questions about his skills, projects, and experience. Everything I tell you is grounded in verified data. What would you like to know?
      </div>
    </div>
    <div class="chat-input-area">
      <input type="text" id="chatInput" placeholder="Ask about skills, projects, experience..." autocomplete="off">
      <button id="chatSendBtn">Send</button>
    </div>
  </div>

  <script src="/static/js/portfolio.js"></script>
</body>
</html>
```

- [ ] **Step 4: Commit**

```bash
git add apps/api/static/ && git commit -m "feat: add portfolio site frontend with chat panel"
```

---

### Task 9: Build HybridDemo Page

**Files:**
- Create: `apps/api/static/demo.html`

The HybridDemo is the user's React component converted to a standalone HTML page. Since the portfolio site uses vanilla HTML/JS (no React build step), we embed React via CDN for just this page.

- [ ] **Step 1: Create demo.html**

Create `apps/api/static/demo.html` containing the user's HybridDemo React component wrapped in a standalone HTML page with React CDN imports (`react`, `react-dom`, `babel-standalone`). Include:
- The full `SCENARIOS`, `computeDerivedFields`, `callClaude`, `Dots`, `StepLog`, and `HybridDemo` components exactly as provided by the user
- A root div and ReactDOM.createRoot render call
- A back-to-portfolio link in the header
- Google Fonts link for Libre Franklin, Fira Code, Playfair Display

The page should be self-contained — no dependency on portfolio.css or portfolio.js.

- [ ] **Step 2: Commit**

```bash
git add apps/api/static/demo.html && git commit -m "feat: add HybridDemo interactive page"
```

---

### Task 10: Update CLAUDE.md

**Files:**
- Modify: `CLAUDE.md`

- [ ] **Step 1: Update CLAUDE.md**

Replace the entire file with content reflecting the portfolio site:

```markdown
# CLAUDE.md

## Project Overview

AI portfolio agent site for Chris Combs. Visitors (employers, recruiters, freelance clients) interact with an AI agent grounded in verified resume/project data. Built on the ai-agent-platform architecture.

## Commands

```bash
# Setup
python -m venv .venv
.venv\Scripts\Activate.ps1          # Windows
pip install -e ".[dev]"
cp .env.example .env                # add GOOGLE_API_KEY

# Run
.venv\Scripts\python -m uvicorn apps.api.main:app --reload
```

No test runner or linter configured yet.

## Architecture

**FastAPI backend** serves static portfolio HTML and a `/api/chat` endpoint. The chat endpoint loads the portfolio agent's system prompt (which includes the full knowledge base from `data/knowledge/*.md`), sends conversation to Gemini, and returns the response.

**No tool calling, no function chaining** — the portfolio agent is a pure conversation agent grounded in its knowledge base.

**Key files:**
- `apps/api/main.py` — App setup, registers portfolio agent
- `apps/api/routes/chat.py` — Simple chat endpoint (~120 lines)
- `apps/api/routes/ui.py` — Serves index.html and demo.html
- `apps/api/static/` — Portfolio frontend (HTML/CSS/JS)
- `core/agents/builtins/portfolio_agent.py` — Agent definition + system prompt
- `data/knowledge/` — Markdown files loaded into agent context
- `core/shared/config.py` — Settings (GOOGLE_API_KEY)

## Content Updates

To update what the agent knows, edit files in `data/knowledge/`. Changes take effect on next server restart (files are loaded at import time in `portfolio_agent.py`).

## Deployment

```bash
# Docker
docker compose up

# Cloud Run
gcloud run deploy portfolio-agent --source . --region us-central1 --project pro-habitat-485707-p7
```

Environment: `GOOGLE_API_KEY` (required)
```

- [ ] **Step 2: Commit**

```bash
git add CLAUDE.md && git commit -m "docs: update CLAUDE.md for portfolio site"
```

---

### Task 11: Clean Up Remaining Unused Files

**Files:**
- Check: `apps/api/routes/tools.py` — still useful for `/api/tools` listing (keep, but it'll return empty)
- Check: `core/tools/builtins/calculator.py` — no longer registered, can keep for future use
- Verify: no broken imports remain

- [ ] **Step 1: Verify no broken imports**

```bash
cd C:/Users/ccdmn/code/portfolio-site && python -c "from apps.api.main import app; print('OK')"
```

Expected: `OK` with no import errors.

- [ ] **Step 2: If import errors, fix them**

Common fixes:
- Remove `tools.py` route from `main.py` if `tool_registry` has broken imports
- Ensure `core/tools/builtins/__init__.py` exists and doesn't import deleted modules

- [ ] **Step 3: Start the server and verify**

```bash
cd C:/Users/ccdmn/code/portfolio-site && .venv/Scripts/python -m uvicorn apps.api.main:app --port 8000
```

Expected: Server starts, visit `http://localhost:8000` and see the portfolio page.

- [ ] **Step 4: Test the chat endpoint**

```bash
curl -X POST http://localhost:8000/api/chat -H "Content-Type: application/json" -d '{"message": "What can Chris build?"}'
```

Expected: JSON response with `reply`, `model`, `session_id`.

- [ ] **Step 5: Final commit**

```bash
git add -A && git commit -m "chore: clean up and verify portfolio site works"
```

---

## Summary

| Task | What it does | Est. effort |
|------|-------------|-------------|
| 1 | Delete old agents/tools/routes | 2 min |
| 2 | Create knowledge base markdown files | 5 min |
| 3 | Create portfolio agent with system prompt | 5 min |
| 4 | Simplify config/deps | 3 min |
| 5 | Rewrite main.py | 2 min |
| 6 | Rewrite chat.py | 5 min |
| 7 | Update UI routes | 2 min |
| 8 | Build portfolio frontend (HTML/CSS/JS) | 15 min |
| 9 | Build HybridDemo page | 10 min |
| 10 | Update CLAUDE.md | 2 min |
| 11 | Clean up and verify | 5 min |
