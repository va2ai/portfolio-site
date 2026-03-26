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
    from .routes.leads import router as leads_router
    from .routes.ui import router as ui_router

    app.mount("/static", StaticFiles(directory="apps/api/static"), name="static")

    app.include_router(health_router)
    app.include_router(agents_router, prefix="/api")
    app.include_router(chat_router, prefix="/api")
    app.include_router(leads_router, prefix="/api")
    app.include_router(ui_router)

    return app


app = create_app()
