import os
import secrets
from pathlib import Path
from dotenv import dotenv_values
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[4]
ENV_FILE = PROJECT_ROOT / ".env"


def _runtime_environment() -> str:
    env_file = dotenv_values(ENV_FILE)
    return (os.getenv("ENVIRONMENT") or env_file.get("ENVIRONMENT") or "development").lower()


def _secret_key_default() -> str:
    env_file = dotenv_values(ENV_FILE)
    environment = _runtime_environment()
    configured = os.getenv("SECRET_KEY") or env_file.get("SECRET_KEY")
    if configured:
        unsafe = configured.lower() in {"knowledge-center-secret-key-2026-prod-safe", "change-me"} or configured.lower().startswith("replace-with-")
        if environment in {"production", "prod"} and (len(configured) < 32 or unsafe):
            raise RuntimeError("生产环境 SECRET_KEY 至少需要 32 个字符")
        return configured
    if environment in {"production", "prod"}:
        raise RuntimeError("生产环境必须设置 SECRET_KEY")
    # 开发环境每次进程启动生成临时密钥，避免把可预测密钥提交到代码库。
    return secrets.token_urlsafe(48)


def _upload_dir_default() -> str:
    env_file = dotenv_values(ENV_FILE)
    environment = _runtime_environment()
    configured = os.getenv("UPLOAD_DIR") or env_file.get("UPLOAD_DIR")
    if configured:
        return configured
    if environment in {"production", "prod"}:
        raise RuntimeError("生产环境必须设置 UPLOAD_DIR")
    return str(PROJECT_ROOT / "apps" / "server" / "uploads")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")

    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://admin:password@localhost:3306/knowledge_center?charset=utf8mb4"
    )
    SECRET_KEY: str = _secret_key_default()
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    UPLOAD_DIR: str = _upload_dir_default()
    MAX_UPLOAD_SIZE_MB: int = 50
    CORS_ORIGINS: str = "http://localhost:3000"


settings = Settings()
