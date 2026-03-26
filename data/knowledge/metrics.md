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
