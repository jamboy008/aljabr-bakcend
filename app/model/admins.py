from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.database.Base import Base


class Admin(Base):
    """Website administration login."""
    __tablename__ = "admins"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(60), unique=True)
    password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    token_version: Mapped[int] = mapped_column(default=0)
