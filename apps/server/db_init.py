"""Local-only table bootstrap. Production must use Alembic migrations."""
from app.core.config import settings


def assert_not_production(environment: str | None = None) -> None:
    env = (environment if environment is not None else settings.ENVIRONMENT) or ""
    if env.lower() in {"production", "prod"}:
        raise SystemExit("Refuse to run db_init.py when ENVIRONMENT=production. Use: python -m alembic upgrade head")


if __name__ == "__main__":
    assert_not_production()
    from app.models.database import engine, Base
    from app.models.entities import *  # noqa: F401,F403
    from app.models.audit import AuditLog  # noqa: F401

    print("Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully.")
