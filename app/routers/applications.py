from uuid import uuid4
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Request
from sqlalchemy import select, func, or_
from app.database.Base import MyDb
from app.model import Applications, Products
from app.scheme.applications import (ApplicationAdd, ApplicationReceipt, ApplicationResponse,
                                      ApplicationUpdate, ApplicationPage, ApplicationStatus)
from app.utils.checker import check_ident, commit
from app.utils.rate_limiting import limiter
from app.utils.security import get_current_admin
from app.utils.telegram import build_message, send_telegram

router = APIRouter(prefix="/applications", tags=["Applications"])


@router.post("/", response_model=ApplicationReceipt, status_code=201)
@limiter.limit("5/minute;30/hour")
def add_application(request: Request, data: ApplicationAdd, db: MyDb, background: BackgroundTasks):
    product = db.scalar(select(Products).where(Products.slug == data.product, Products.is_active.is_(True)))
    if product is None:
        raise HTTPException(422, "Mahsulot topilmadi yoki faol emas")
    obj = Applications(**data.model_dump(exclude={"product"}), product_id=product.id, reference=str(uuid4()))
    db.add(obj)
    commit(db)
    background.add_task(send_telegram, build_message(
        reference=obj.reference, product=product.name, plan=data.plan,
        name=data.name, phone=data.phone, description=data.description))
    return {"reference": obj.reference}


@router.get("/", response_model=ApplicationPage)
def list_applications(db: MyDb, user=Depends(get_current_admin),
                      page: int = Query(1, ge=1), size: int = Query(20, ge=1, le=100),
                      status: ApplicationStatus | None = None, product_id: int | None = Query(None, gt=0),
                      search: str | None = Query(None, max_length=100)):
    filters = []
    if status:
        filters.append(Applications.status == status)
    if product_id:
        filters.append(Applications.product_id == product_id)
    if search:
        filters.append(or_(Applications.name.contains(search, autoescape=True),
                           Applications.phone.contains(search, autoescape=True)))
    total = db.scalar(select(func.count()).select_from(Applications).where(*filters))
    items = (db.scalars(select(Applications).where(*filters).order_by(Applications.id.desc())
                        .offset((page - 1) * size).limit(size))).all()
    return {"items": items, "total": total, "page": page, "size": size}


@router.get("/stats")
def stats(db: MyDb, user=Depends(get_current_admin)):
    rows = (db.execute(select(Applications.status, func.count()).group_by(Applications.status))).all()
    counts = {key: 0 for key in ("new", "contacted", "in_progress", "completed", "rejected")}
    counts.update(dict(rows))
    return {"total": sum(counts.values()), "by_status": counts}


@router.get("/{application_id}", response_model=ApplicationResponse)
def get_application(application_id: int, db: MyDb, user=Depends(get_current_admin)):
    return check_ident(db, Applications, application_id)


@router.put("/{application_id}", response_model=ApplicationResponse)
def update_application(application_id: int, data: ApplicationUpdate, db: MyDb, user=Depends(get_current_admin)):
    obj = check_ident(db, Applications, application_id)
    for key, value in data.model_dump().items():
        setattr(obj, key, value)
    commit(db)
    db.refresh(obj)
    return obj


@router.delete("/{application_id}", status_code=204)
def delete_application(application_id: int, db: MyDb, user=Depends(get_current_admin)):
    obj = check_ident(db, Applications, application_id)
    db.delete(obj)
    commit(db)