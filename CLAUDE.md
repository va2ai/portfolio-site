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
