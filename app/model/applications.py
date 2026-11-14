from datetime import datetime, timezone
from sqlalchemy import String, Text, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.database.Base import Base


class Applications(Base):
    __tablename__ = "applications"
    id: Mapped[int] = mapped_column(primary_key=True)
    reference: Mapped[str] = mapped_column(String(36), unique=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="RESTRICT"), index=True)
    name: Mapped[str] = mapped_column(String(100))
    phone: Mapped[str] = mapped_column(String(20), index=True)
    plan: Mapped[str] = mapped_column(String(20))
    description: Mapped[str] = mapped_column(Text)
    consent: Mapped[bool] = mapped_column(Boolean)
    status: Mapped[str] = mapped_column(String(20), default="new", index=True)
    notes: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
