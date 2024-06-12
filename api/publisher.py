from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from api.utils import ep_err_msg, get_db, request_auth
from db.tables.publsiher_entity import PublisherEntity

router = APIRouter(
    responses={status.HTTP_404_NOT_FOUND: {"Description": ep_err_msg}},
    dependencies=[Depends(request_auth)],
)


class PublisherBase(BaseModel):
    name: str
    url: str
    favicon_url: Optional[str] = None
    cover_url: Optional[str] = None
    background_color: Optional[str] = None
    enabled: bool
    score: float


class PublisherCreate(PublisherBase):
    pass


class Publisher(PublisherBase):
    id: int

    class Config:
        from_attributes = True


@router.get("/api/publisher", response_model=List[Publisher])
async def read_publishers(
    skip: int = 0, limit: int = 10, db: Session = Depends(get_db)
):
    publishers = db.query(PublisherEntity).offset(skip).limit(limit).all()
    return publishers


@router.get("/api/publisher/{id}", response_model=Publisher)
async def read_publisher(id: int, db: Session = Depends(get_db)):
    publisher = db.query(PublisherEntity).filter(PublisherEntity.id == id).first()
    if publisher is None:
        raise HTTPException(status_code=404, detail="Publisher not found")
    return publisher


@router.post("/api/publisher/{id}", response_model=Publisher)
async def create_or_update_publisher(
    id: int, publisher: PublisherCreate, db: Session = Depends(get_db)
):
    db_publisher = db.query(PublisherEntity).filter(PublisherEntity.id == id).first()
    if db_publisher is None:
        db_publisher = PublisherEntity(id=id, **publisher.dict())
    else:
        for key, value in publisher.dict().items():
            setattr(db_publisher, key, value)
    db.add(db_publisher)
    db.commit()
    db.refresh(db_publisher)
    return db_publisher
