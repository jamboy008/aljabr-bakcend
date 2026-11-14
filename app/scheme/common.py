import re
from pydantic import BaseModel, ConfigDict


class Schema(BaseModel):
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True, extra="forbid")


def normalize_phone(value: str) -> str:
    if not re.fullmatch(r"\+?[0-9 ()-]+", value):
        raise ValueError("Telefon raqami noto'g'ri")
    digits = re.sub(r"\D", "", value)
    if len(digits) == 9:
        digits = "998" + digits
    if not 9 <= len(digits) <= 15:
        raise ValueError("Telefon raqami 9-15 raqamdan iborat bo'lishi kerak")
    return "+" + digits
