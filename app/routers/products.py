from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from app.database.Base import MyDb
from app.model import Products
from app.scheme.products import ProductAdd, ProductResponse
from app.utils.checker import check_ident, commit
from app.utils.security import get_current_admin

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("/", response_model=list[ProductResponse])
def list_products(db: MyDb, page: int = Query(1, ge=1), size: int = Query(50, ge=1, le=100)):
    return (db.scalars(select(Products).where(Products.is_active.is_(True))
                            .order_by(Products.id).offset((page - 1) * size).limit(size))).all()


@router.get("/manage", response_model=list[ProductResponse])
def manage_products(db: MyDb, user=Depends(get_current_admin),
                          page: int = Query(1, ge=1), size: int = Query(50, ge=1, le=100)):
    return (db.scalars(select(Products).order_by(Products.id)
                            .offset((page - 1) * size).limit(size))).all()


@router.post("/", response_model=ProductResponse, status_code=201)
def add_product(data: ProductAdd, db: MyDb, user=Depends(get_current_admin)):
    obj = Products(**data.model_dump())
    db.add(obj)
    commit(db)
    return obj


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, data: ProductAdd, db: MyDb,
                         user=Depends(get_current_admin)):
    obj = check_ident(db, Products, product_id)
    for key, value in data.model_dump().items():
        setattr(obj, key, value)
    commit(db)
    return obj


@router.delete("/{product_id}", status_code=204)
def delete_product(product_id: int, db: MyDb, user=Depends(get_current_admin)):
    obj = check_ident(db, Products, product_id)
    db.delete(obj)
    commit(db)
