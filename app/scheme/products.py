from pydantic import Field
from app.scheme.common import Schema


class ProductAdd(Schema):
    slug: str = Field(min_length=2, max_length=60, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    name: str = Field(min_length=2, max_length=120)
    description: str = Field(default="", max_length=5000)
    is_active: bool = True


class ProductResponse(ProductAdd):
    id: int
