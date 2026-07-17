from __future__ import annotations

import os
from pathlib import Path

from .runtime_settings import load_runtime_settings


BASE_DIR = Path(__file__).resolve().parents[2]
RUNTIME_SETTINGS = load_runtime_settings()
DATABASE_URL = os.getenv("DATABASE_URL") or str(RUNTIME_SETTINGS.get("database_url") or "mysql+pymysql://onewiki:onewiki_dev_password@127.0.0.1:3306/onewiki?charset=utf8mb4")
FILE_STORAGE_ROOT = Path(os.getenv("FILE_STORAGE_ROOT", str(BASE_DIR / "storage"))).expanduser()
MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", str(RUNTIME_SETTINGS.get("max_upload_size_mb", 100))))
SESSION_DAYS = int(os.getenv("SESSION_DAYS", str(RUNTIME_SETTINGS.get("session_days", 14))))
AI_ENABLED = os.getenv("AI_ENABLED", str(RUNTIME_SETTINGS.get("ai_enabled", False))).lower() == "true"
LLM_BASE_URL = os.getenv("LLM_BASE_URL", str(RUNTIME_SETTINGS.get("llm_base_url", ""))).rstrip("/")
LLM_API_KEY = os.getenv("LLM_API_KEY", str(RUNTIME_SETTINGS.get("llm_api_key", "")))
LLM_MODEL = os.getenv("LLM_MODEL", str(RUNTIME_SETTINGS.get("llm_model", "")))

FILE_STORAGE_ROOT.mkdir(parents=True, exist_ok=True)
for name in ("objects", "temp", "extracted", "thumbnails"):
    (FILE_STORAGE_ROOT / name).mkdir(parents=True, exist_ok=True)
