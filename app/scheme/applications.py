from datetime import datetime
from typing import Literal
from pydantic import Field, field_validator
from app.scheme.common import Schema, normalize_phone

ApplicationStatus = Literal["new", "contacted", "in_progress", "completed", "rejected"]


class ApplicationAdd(Schema):
    product: str = Field(min_length=2, max_length=60)
    plan: Literal["standard", "pro"]
    name: str = Field(min_length=2, max_length=100)
    phone: str = Field(max_length=25)
    description: str = Field(min_length=10, max_length=3000)
    consent: Literal[True]
    _phone = field_validator("phone")(normalize_phone)


class ApplicationReceipt(Schema):
    reference: str
    message: str = "Arizangiz qabul qilindi. Tez orada bog'lanamiz."


class ApplicationUpdate(Schema):
    status: ApplicationStatus
    notes: str = Field(default="", max_length=5000)


class ApplicationResponse(Schema):
    id: int
    reference: str
    product_id: int
    plan: str
    name: str
    phone: str
    description: str
    consent: bool
    status: ApplicationStatus
    notes: str
    created_at: datetime
    updated_at: datetime


class ApplicationPage(Schema):
    items: list[ApplicationResponse]
    total: int
    page: int
    size: int
