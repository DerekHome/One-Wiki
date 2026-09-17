import copy
import re
from typing import Any, Dict, List

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.entities import SystemSetting

DEFAULT_ALLOWED_EXTENSIONS = [
    ".md", ".markdown", ".txt", ".png", ".jpg", ".jpeg", ".gif", ".webp",
    ".pdf", ".zip", ".docx", ".xlsx", ".csv", ".html", ".htm",
]
BLOCKED_EXTENSIONS = {
    ".exe", ".bat", ".cmd", ".com", ".msi", ".js", ".mjs", ".php", ".phtml",
    ".sh", ".ps1", ".dll", ".so", ".svg",
}
EDITABLE_KEYS = {
    "site_name",
    "max_upload_size_mb",
    "allowed_extensions",
    "allow_registration",
    "default_space_visibility",
    "jwt_expire_minutes",
}
EXT_RE = re.compile(r"^\.[A-Za-z0-9]{1,10}$")
VISIBILITY_VALUES = {"public", "internal", "private"}

_cache: Dict[str, Any] = {}


def default_settings() -> Dict[str, Any]:
    return {
        "site_name": "企业知识中心 (Knowledge Hub)",
        "storage_type": "local",
        "storage_path": settings.UPLOAD_DIR,
        "max_upload_size_mb": int(settings.MAX_UPLOAD_SIZE_MB),
        "allowed_extensions": list(DEFAULT_ALLOWED_EXTENSIONS),
        "allow_registration": True,
        "default_space_visibility": "internal",
        "jwt_expire_minutes": int(settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    }


def _public_view(data: Dict[str, Any]) -> Dict[str, Any]:
    view = copy.deepcopy(data)
    view["storage_type"] = "local"
    view["storage_path"] = settings.UPLOAD_DIR
    return view


def reset_runtime_cache() -> None:
    _cache.clear()
    _cache.update(default_settings())


def get_cached_settings() -> Dict[str, Any]:
    if not _cache:
        _cache.update(default_settings())
    return _public_view(_cache)


def load_from_db(db: Session) -> Dict[str, Any]:
    merged = default_settings()
    try:
        rows = db.query(SystemSetting).all()
    except Exception:
        _cache.clear()
        _cache.update(merged)
        return get_cached_settings()
    for row in rows:
        if row.key in EDITABLE_KEYS:
            merged[row.key] = row.value
    _cache.clear()
    _cache.update(merged)
    return get_cached_settings()


def _normalize_extensions(raw: Any) -> List[str]:
    if not isinstance(raw, list):
        raise HTTPException(status_code=422, detail={"code": "INVALID_SETTINGS", "message": "allowed_extensions 必须是数组"})
    normalized: List[str] = []
    seen = set()
    for item in raw:
        ext = str(item or "").strip().lower()
        if not ext:
            continue
        if not ext.startswith("."):
            ext = f".{ext}"
        if not EXT_RE.match(ext):
            raise HTTPException(status_code=422, detail={"code": "INVALID_EXTENSION", "message": f"非法扩展名: {item}"})
        if ext in BLOCKED_EXTENSIONS:
            raise HTTPException(status_code=422, detail={"code": "BLOCKED_EXTENSION", "message": f"不允许的扩展名: {ext}"})
        if ext not in seen:
            seen.add(ext)
            normalized.append(ext)
    if not normalized:
        raise HTTPException(status_code=422, detail={"code": "INVALID_SETTINGS", "message": "至少保留一种允许的扩展名"})
    return normalized


def sanitize_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    cleaned: Dict[str, Any] = {}
    if "site_name" in payload:
        name = str(payload.get("site_name") or "").strip()
        if not name or len(name) > 128:
            raise HTTPException(status_code=422, detail={"code": "INVALID_SETTINGS", "message": "站点名称长度无效"})
        cleaned["site_name"] = name
    if "max_upload_size_mb" in payload:
        try:
            size = int(payload["max_upload_size_mb"])
        except (TypeError, ValueError):
            raise HTTPException(status_code=422, detail={"code": "INVALID_SETTINGS", "message": "上传大小限制无效"})
        if size < 1 or size > 500:
            raise HTTPException(status_code=422, detail={"code": "INVALID_SETTINGS", "message": "上传大小限制需在 1–500 MB"})
        cleaned["max_upload_size_mb"] = size
    if "allowed_extensions" in payload:
        cleaned["allowed_extensions"] = _normalize_extensions(payload["allowed_extensions"])
    if "allow_registration" in payload:
        cleaned["allow_registration"] = bool(payload["allow_registration"])
    if "default_space_visibility" in payload:
        vis = str(payload.get("default_space_visibility") or "").strip().lower()
        if vis not in VISIBILITY_VALUES:
            raise HTTPException(status_code=422, detail={"code": "INVALID_SETTINGS", "message": "默认空间可见性无效"})
        cleaned["default_space_visibility"] = vis
    if "jwt_expire_minutes" in payload:
        try:
            minutes = int(payload["jwt_expire_minutes"])
        except (TypeError, ValueError):
            raise HTTPException(status_code=422, detail={"code": "INVALID_SETTINGS", "message": "JWT 有效期无效"})
        if minutes < 5 or minutes > 10080:
            raise HTTPException(status_code=422, detail={"code": "INVALID_SETTINGS", "message": "JWT 有效期需在 5–10080 分钟"})
        cleaned["jwt_expire_minutes"] = minutes
    return cleaned


def save_to_db(db: Session, payload: Dict[str, Any]) -> Dict[str, Any]:
    cleaned = sanitize_payload(payload)
    current = default_settings()
    current.update({k: v for k, v in get_cached_settings().items() if k in EDITABLE_KEYS})
    current.update(cleaned)
    for key in EDITABLE_KEYS:
        row = db.query(SystemSetting).filter(SystemSetting.key == key).first()
        if row is None:
            db.add(SystemSetting(key=key, value=current[key]))
        else:
            row.value = current[key]
    db.commit()
    return load_from_db(db)
