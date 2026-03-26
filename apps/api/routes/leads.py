"""Lead capture endpoint — stores contact info from ElevenLabs voice agent and website."""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(tags=["leads"])

# In-memory lead store (consistent with session storage pattern in chat.py)
_leads: list[dict[str, Any]] = []


class LeadRequest(BaseModel):
    name: str
    email: str = ""
    company: str = ""
    role_or_project: str = ""
    visitor_type: str = ""  # recruiter | hiring_manager | freelance_client | general
    lead_type: str = "contact"  # contact | callback_request
    preferred_time: str = ""
    topic: str = ""
    priority: str = "normal"  # high | normal
    source: str = "website"  # website | elevenlabs_voice_agent


@router.post("/leads")
async def capture_lead(req: LeadRequest):
    lead_id = str(uuid.uuid4())
    lead = {
        "lead_id": lead_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **req.model_dump(exclude_defaults=False),
    }
    _leads.append(lead)
    logger.info(f"Lead captured: {lead_id} — {req.name} ({req.visitor_type or 'unknown'})")
    return {"status": "saved", "lead_id": lead_id}


@router.get("/leads")
async def list_leads():
    return {"leads": _leads, "count": len(_leads)}
