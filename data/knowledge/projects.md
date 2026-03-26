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
