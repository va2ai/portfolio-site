from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up...")

    # Register built-in tools
    from core.tools.registry import tool_registry
    from core.tools.builtins.web_search import WebSearchTool
    from core.tools.builtins.calculator import CalculatorTool
    from core.tools.builtins.tavily_search import TavilySearchTool

    tool_registry.register(WebSearchTool())
    tool_registry.register(CalculatorTool())
    tool_registry.register(TavilySearchTool())
    logger.info(f"Registered tools: {tool_registry.tool_names}")

    yield
    logger.info("Shutting down...")


def create_app() -> FastAPI:
    app = FastAPI(title="ai-agent-platform", version="0.1.0", lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Import and include routers
    from .routes.health import router as health_router
    from .routes.agents import router as agents_router
    from .routes.tools import router as tools_router
    from .routes.retrieval import router as retrieval_router
    from .routes.chat import router as chat_router
    from .routes.search import router as search_router
    from .routes.ui import router as ui_router

    app.include_router(health_router)
    app.include_router(agents_router, prefix="/api")
    app.include_router(tools_router, prefix="/api")
    app.include_router(retrieval_router, prefix="/api")
    app.include_router(chat_router, prefix="/api")
    app.include_router(search_router, prefix="/api")
    app.include_router(ui_router)

    return app


app = create_app()
