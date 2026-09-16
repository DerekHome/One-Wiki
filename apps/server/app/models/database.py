from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings


def normalize_database_url(url: str) -> str:
    if url.startswith("mysql://"):
        url = "mysql+pymysql://" + url[len("mysql://"):]
    if url.startswith("mysql+pymysql://") and "charset=" not in url:
        joiner = "&" if "?" in url else "?"
        url = f"{url}{joiner}charset=utf8mb4"
    return url


engine = create_engine(normalize_database_url(settings.DATABASE_URL), pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
