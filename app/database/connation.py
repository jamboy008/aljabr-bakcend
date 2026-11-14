from sqlalchemy import URL
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.utils.config import settings

if settings.DATABASE_URL:
    engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
else:
    database_url = URL.create(
        "mysql+pymysql", username=settings.DB_USERNAME, password=settings.DB_PASS,
        host=settings.DB_HOST, port=settings.DB_PORT, database=settings.DB_NAME,
        query={"charset": "utf8mb4"},
    )
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(engine, expire_on_commit=False)


def get_db():
    with SessionLocal() as db:
        try:
            yield db
        except Exception:
            db.rollback()
            raise