from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError


def check_ident(db, model, ident):
    obj = db.get(model, ident)
    if obj is None:
        raise HTTPException(404, "Object not found")
    return obj


def commit(db):
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Duplicate value or object is still in use") from None
