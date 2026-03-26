from __future__ import annotations

import os
from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter()

# Path to the static index.html
UI_FILE_PATH = os.path.join(os.path.dirname(__file__), "..", "static", "index.html")


@router.get("/", response_class=FileResponse)
async def index():
    return FileResponse(UI_FILE_PATH)
