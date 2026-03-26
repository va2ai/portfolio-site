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
