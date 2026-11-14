"""Run from the project root: python -m app.cli init-db / create-admin."""
import argparse
import getpass
from sqlalchemy import select
from app.database.Base import Base
from app.database.connation import engine, SessionLocal
from app.model import Admin, Products
from app.utils.security import hash_password, revoke_sessions

PRODUCTS = {
    "websites": "Veb-sayt yaratish", "crm": "CRM tizimi", "erp": "ERP tizimi",
    "mobile": "Mobil ilova", "ai": "Sun'iy intellekt yechimlari",
    "ecommerce": "Elektron savdo", "telegram": "Telegram bot",
    "telegram-mini-app": "Telegram Mini App",
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["init-db", "create-admin", "reset-password"])
    args = parser.parse_args()
    try:
        if args.command == "init-db":
            Base.metadata.create_all(engine)
            with SessionLocal() as db:
                existing = set(db.scalars(select(Products.slug)))
                for slug, name in PRODUCTS.items():
                    if slug not in existing:
                        db.add(Products(slug=slug, name=name))
                db.commit()
            print("MySQL tables and services are ready.")
            return
        username = input("Admin username: ").strip()
        if not 3 <= len(username) <= 60:
            parser.error("Username must be 3-60 characters")
        password = getpass.getpass("Password (12-128 characters): ")
        if not 12 <= len(password) <= 128:
            parser.error("Password must be 12-128 characters")
        if password != getpass.getpass("Repeat password: "):
            parser.error("Passwords do not match")
        with SessionLocal() as db:
            admin = db.scalar(select(Admin).where(Admin.username == username).with_for_update())
            if args.command == "create-admin":
                if admin:
                    parser.error("Username already exists")
                db.add(Admin(username=username, password=hash_password(password)))
            else:
                if not admin:
                    parser.error("Admin not found")
                admin.password = hash_password(password)
                revoke_sessions(db, admin)
            db.commit()
        print("Admin saved.")
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
