from __future__ import annotations

import json
import os
from pathlib import Path
from threading import Lock
from typing import Any


_lock = Lock()


def settings_path() -> Path:
    root = Path(os.getenv("FILE_STORAGE_ROOT", str(Path(__file__).resolve().parents[2] / "storage"))).expanduser()
    root.mkdir(parents=True, exist_ok=True)
    return root / "runtime-settings.json"


def load_runtime_settings() -> dict[str, Any]:
    path = settings_path()
    if not path.exists():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def save_runtime_settings(changes: dict[str, Any]) -> dict[str, Any]:
    with _lock:
        current = load_runtime_settings()
        for key, value in changes.items():
            if value is not None:
                current[key] = value
        path = settings_path()
        temporary = path.with_suffix(".tmp")
        temporary.write_text(json.dumps(current, ensure_ascii=False, indent=2), encoding="utf-8")
        temporary.replace(path)
        return current


def public_runtime_settings() -> dict[str, Any]:
    settings = load_runtime_settings()
    return {
        "site_name": settings.get("site_name", "One WIKI"),
        "registration_enabled": bool(settings.get("registration_enabled", True)),
    }


def masked_runtime_settings() -> dict[str, Any]:
    settings = load_runtime_settings()
    database_url = str(settings.get("database_url", ""))
    api_key = str(settings.get("llm_api_key", ""))
    return {
        **public_runtime_settings(),
        "database_url_configured": bool(database_url),
        "database_url_masked": mask_connection_url(database_url),
        "database_managed_by_environment": bool(os.getenv("DATABASE_URL")),
        "ai_enabled": bool(settings.get("ai_enabled", False)),
        "llm_base_url": settings.get("llm_base_url", ""),
        "llm_model": settings.get("llm_model", ""),
        "llm_api_key_configured": bool(api_key or os.getenv("LLM_API_KEY")),
        "session_days": int(settings.get("session_days", os.getenv("SESSION_DAYS", "14"))),
        "max_upload_size_mb": int(settings.get("max_upload_size_mb", os.getenv("MAX_UPLOAD_SIZE_MB", "100"))),
    }


def mask_connection_url(value: str) -> str:
    if not value:
        return ""
    if "@" not in value or "://" not in value:
        return value
    scheme, remainder = value.split("://", 1)
    credentials, host = remainder.rsplit("@", 1)
    username = credentials.split(":", 1)[0]
    return f"{scheme}://{username}:******@{host}"
