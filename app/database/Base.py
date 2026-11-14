from typing import Annotated
from fastapi import Depends
from sqlalchemy.orm import Session
from sqlalchemy.orm import DeclarativeBase
from app.database.connation import get_db


class Base(DeclarativeBase):
    pass


MyDb = Annotated[Session, Depends(get_db)]
