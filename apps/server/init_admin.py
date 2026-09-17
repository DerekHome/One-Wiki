"""Create or promote the first system administrator.

Usage: python init_admin.py --username admin --password 'change-me'
"""
import argparse

from app.models.database import SessionLocal
from app.models.entities import User
from app.core.security import get_password_hash


def main() -> None:
    parser = argparse.ArgumentParser(description="Initialize a knowledge-center administrator")
    parser.add_argument("--username", required=True)
    parser.add_argument("--password", required=True)
    args = parser.parse_args()

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == args.username).first()
        if user is None:
            user = User(username=args.username, hashed_password=get_password_hash(args.password), role="admin", is_active=True)
            db.add(user)
        else:
            user.role = "admin"
            user.is_active = True
            user.hashed_password = get_password_hash(args.password)
            user.security_stamp = int(getattr(user, "security_stamp", 0) or 0) + 1
        db.commit()
        print(f"Administrator ready: {user.username}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
