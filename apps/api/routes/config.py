from __future__ import annotations

from fastapi import APIRouter
from core.shared.config import settings

router = APIRouter()


@router.get("/config")
async def public_config():
    """Return public-safe configuration for the frontend."""
    return {
        "elevenlabs_agent_id": settings.elevenlabs_agent_id,
    }
