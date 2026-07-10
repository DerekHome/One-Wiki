from __future__ import annotations

import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'knowledge.db'}")
FILE_STORAGE_ROOT = Path(os.getenv("FILE_STORAGE_ROOT", str(BASE_DIR / "storage"))).expanduser()
MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "100"))
SESSION_DAYS = int(os.getenv("SESSION_DAYS", "14"))
AI_ENABLED = os.getenv("AI_ENABLED", "false").lower() == "true"
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "").rstrip("/")
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "")

FILE_STORAGE_ROOT.mkdir(parents=True, exist_ok=True)
for name in ("objects", "temp", "extracted", "thumbnails"):
    (FILE_STORAGE_ROOT / name).mkdir(parents=True, exist_ok=True)
