from __future__ import annotations

import hashlib
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile

from .config import FILE_STORAGE_ROOT, MAX_UPLOAD_SIZE_MB


class LocalFileStorage:
    def _path(self, storage_key: str) -> Path:
        candidate = (FILE_STORAGE_ROOT / storage_key).resolve()
        root = FILE_STORAGE_ROOT.resolve()
        if root not in candidate.parents and candidate != root:
            raise HTTPException(400, "非法文件路径")
        return candidate

    async def save(self, upload: UploadFile) -> tuple[str, int, str]:
        asset_id = uuid4().hex
        storage_key = f"objects/{asset_id[:2]}/{asset_id[2:4]}/{asset_id}"
        target = self._path(storage_key)
        target.parent.mkdir(parents=True, exist_ok=True)
        temp = self._path(f"temp/{asset_id}.upload")
        total = 0
        digest = hashlib.sha256()
        with temp.open("wb") as output:
            while chunk := await upload.read(1024 * 1024):
                total += len(chunk)
                if total > MAX_UPLOAD_SIZE_MB * 1024 * 1024:
                    output.close()
                    temp.unlink(missing_ok=True)
                    raise HTTPException(413, f"文件不能超过 {MAX_UPLOAD_SIZE_MB} MB")
                digest.update(chunk)
                output.write(chunk)
        temp.replace(target)
        return storage_key, total, digest.hexdigest()

    def open(self, storage_key: str):
        path = self._path(storage_key)
        if not path.exists():
            raise HTTPException(404, "文件不存在")
        return path


storage = LocalFileStorage()
