# Projects

## 1. AI Agent Orchestration Platform
**Purpose:** Multi-agent coordination system serving as reference architecture for enterprise agent systems.
**Architecture:** Parallel AI critics that run simultaneously, iterative refinement loops, convergence logic that determines when agents agree, pub/sub event bus for communication, tool-use guardrails, and traceable run history.
**Testing:** 76 test functions across 6 test files, 75+ automated tests total.
**Tech stack:** Python, FastAPI, LangChain, React/TypeScript, Docker, WebSockets, Pydantic.
**Key feature:** Agents check each other's work before producing final output. Safety rules prevent bad outputs from reaching users.

## 2. RAG Decision Analysis System
**Purpose:** Production pipeline for extracting and querying legal decisions from the Board of Veterans' Appeals.
**Architecture:** Hybrid search combining pgvector vector similarity with keyword matching. Citation-backed synthesis that shows exactly where every answer comes from. Graph-lite relational schema for connecting related decisions.
**Validation:** Tested against an outcome-balanced BVA decision corpus (20 decisions balanced across granted, denied, and remanded outcomes).
**Tech stack:** Python, PostgreSQL, pgvector, Gemini 2.0 Flash, Docker.
**Key feature:** Every answer is traceable to source documents and can be audited.

## 3. V2V Claims Intelligence Platform
**Live URL:** https://vaclaims-194006.web.app
**Purpose:** Full-stack consumer platform helping veterans build stronger VA disability claims.
**Features:** AI-powered BVA Search, Nexus Scout (finds connections between conditions and service), Decision Deconstructor (breaks down complex legal decisions), and contextual chat.
**Architecture:** React frontend with Vite, Firebase Hosting, Firestore data layer, GCP Cloud Run backend with Gemini integration.
**Tech stack:** React, TypeScript, Firebase, GCP Cloud Run, Gemini.
**Key feature:** Real users access this platform to understand VA disability claim decisions.

## 4. MCP Toolbox Server
**Purpose:** Plugin-based Model Context Protocol server providing tools to AI assistants.
**Scope:** 33 tools across 5 plugins: Gemini (AI generation), FAL (image/video generation), Reddit (content access), R2 (cloud storage), and Projects (project management).
**Deployment:** GCP Cloud Run with Secret Manager integration for secure credential handling.
**Tech stack:** Python, FastMCP framework, GCP Cloud Run.
**Key feature:** Demonstrates ability to build standardized tool interfaces for AI systems.

## 5. Edge Deep Research Agent
**Purpose:** Autonomous research agent that performs multi-round web research at global scale.
**Architecture:** Deployed on Cloudflare Workers for edge computing. Performs source quality scoring, conflict detection, and hallucination mitigation. Returns citation-backed synthesis with structured responses.
**Tech stack:** TypeScript, Cloudflare Workers, REST APIs, JSON Schemas.
**Key feature:** Sub-second latency targets with global distribution.

## 6. LLM Compaction Benchmark
**Purpose:** Evaluation framework for comparing AI model performance on text compaction tasks.
**Scope:** 36 model combinations tested across 6 Gemini models.
**Results:** Prompt engineering improved quality scores from 70% to 97%+ with 100% fact recall. Quality retention ranged from 76.5% to 132.3%. Smaller models sometimes beat larger ones.
**Tech stack:** Python, Gemini API, Chart.js for visualization.
**Key feature:** Demonstrates rigorous, data-driven approach to AI model selection.

## 7. Hybrid Hallucination Reduction Demo
**Live Demo:** Available on portfolio site at /demo
**Purpose:** Interactive side-by-side comparison showing that architecture beats model size. An expensive model with raw data vs the cheapest model with pre-validated, pre-computed data.
**Architecture:** Validate → Compute (deterministic JS) → Guard nulls → Constrained generate. 24 financial analytics scenarios covering LTV:CAC, blended ROAS, cash runway, cohort retention, multi-product margin, break-even analysis, and more.
**Key result:** The cheapest model with hybrid architecture consistently outperforms the most expensive model running blind — correct numbers at a fraction of the cost.

## 8. Portfolio Agent Site
**Live URL:** (this site)
**Purpose:** AI portfolio agent that represents Chris to employers and clients. Visitors interact with a conversational agent grounded in verified resume/project data.
**Architecture:** FastAPI backend on Cloud Run, Gemini-powered chat agent with knowledge base loaded from markdown files, vanilla HTML/CSS/JS frontend with slide-out chat panel.
**Key feature:** The site itself IS the portfolio piece — built with the same stack it demonstrates.
