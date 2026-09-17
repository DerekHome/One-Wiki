import os
import threading
import time
from typing import Dict, Tuple

from fastapi import HTTPException, Request, status

from app.core.config import settings


class LoginLimiter:
    """进程内登录失败计数。多实例部署时请改为 Redis 等共享存储。"""

    def __init__(self, max_failures: int = 8, window_seconds: int = 900, lockout_seconds: int = 900):
        self.max_failures = max_failures
        self.window_seconds = window_seconds
        self.lockout_seconds = lockout_seconds
        self._failures: Dict[str, Tuple[int, float]] = {}
        self._lockouts: Dict[str, float] = {}
        self._lock = threading.Lock()

    def _disabled(self) -> bool:
        env = (settings.ENVIRONMENT or "").lower()
        return env in {"test", "testing"} or bool(os.environ.get("PYTEST_CURRENT_TEST"))

    @staticmethod
    def client_ip(request: Request) -> str:
        if request.client and request.client.host:
            return request.client.host
        return "unknown"

    def _key(self, request: Request, username: str) -> str:
        return f"{self.client_ip(request)}:{(username or '').strip().lower()}"

    def check(self, request: Request, username: str) -> None:
        if self._disabled():
            return
        key = self._key(request, username)
        now = time.monotonic()
        with self._lock:
            until = self._lockouts.get(key)
            if until and until > now:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={"code": "LOGIN_LOCKED", "message": "登录失败次数过多，请稍后再试"},
                )
            if until:
                self._lockouts.pop(key, None)

    def record_failure(self, request: Request, username: str) -> None:
        if self._disabled():
            return
        key = self._key(request, username)
        now = time.monotonic()
        with self._lock:
            count, started = self._failures.get(key, (0, now))
            if now - started > self.window_seconds:
                count, started = 0, now
            count += 1
            self._failures[key] = (count, started)
            if count >= self.max_failures:
                self._lockouts[key] = now + self.lockout_seconds
                self._failures.pop(key, None)

    def reset(self, request: Request, username: str) -> None:
        key = self._key(request, username)
        with self._lock:
            self._failures.pop(key, None)
            self._lockouts.pop(key, None)

    def reset_all(self) -> None:
        with self._lock:
            self._failures.clear()
            self._lockouts.clear()


login_limiter = LoginLimiter()
