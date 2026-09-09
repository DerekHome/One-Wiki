from app.models.database import engine, Base
from app.models.entities import *
from app.models.audit import AuditLog

print("Initializing database tables...")
Base.metadata.create_all(bind=engine)
print("Database initialized successfully.")
