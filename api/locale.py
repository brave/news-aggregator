from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from api.utils import ep_err_msg, get_db, request_auth
from db.tables.locales_entity import LocaleEntity

router = APIRouter(
    responses={status.HTTP_404_NOT_FOUND: {"Description": ep_err_msg}},
    dependencies=[Depends(request_auth)],
)


class LocaleBase(BaseModel):
    name: str
    locale: str


class LocaleCreate(LocaleBase):
    pass


class Locale(LocaleBase):
    id: int
    created: datetime
    modified: datetime

    class Config:
        from_attributes = True


@router.get("/api/locale", response_model=List[Locale])
async def get_locales(db: Session = Depends(get_db)):
    locales = db.query(LocaleEntity).all()
    return locales


@router.post("/api/locale", response_model=Locale)
async def create_locale(locale: LocaleCreate, db: Session = Depends(get_db)):
    db_locale = LocaleEntity(**locale.dict())
    db.add(db_locale)
    db.commit()
    db.refresh(db_locale)
    return db_locale
