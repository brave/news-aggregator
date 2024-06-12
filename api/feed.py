from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from api.utils import ep_err_msg, get_db, request_auth
from db.tables.feed_entity import FeedEntity
from db.tables.feed_locales_entity import FeedLocaleEntity
from db.tables.locales_entity import LocaleEntity

router = APIRouter(
    responses={status.HTTP_404_NOT_FOUND: {"Description": ep_err_msg}},
    dependencies=[Depends(request_auth)],
)


class FeedBase(BaseModel):
    url: str
    url_hash: str
    publisher_id: int
    category: str
    enabled: bool
    og_images: bool
    max_entries: int


class FeedCreate(FeedBase):
    pass


class Feed(FeedBase):
    id: int
    created: str
    modified: str

    class Config:
        from_attributes = True


@router.get("/api/feed", response_model=List[Feed])
async def get_feeds(locale: Optional[str] = None, db: Session = Depends(get_db)):
    if locale:
        feeds = (
            db.query(FeedEntity)
            .join(FeedLocaleEntity)
            .join(LocaleEntity)
            .filter(LocaleEntity.locale == locale)
            .all()
        )
    else:
        feeds = db.query(FeedEntity).all()
    return feeds


@router.get("/api/feed/{id}", response_model=Feed)
async def get_feed(id: int, db: Session = Depends(get_db)):
    feed = db.query(FeedEntity).filter(FeedEntity.id == id).first()
    if feed is None:
        raise HTTPException(status_code=404, detail="Feed not found")
    return feed


@router.post("/api/feed/{id}", response_model=Feed)
async def update_feed(id: int, feed: FeedCreate, db: Session = Depends(get_db)):
    db_feed = db.query(FeedEntity).filter(FeedEntity.id == id).first()
    if db_feed:
        for key, value in feed.dict().items():
            setattr(db_feed, key, value)
    else:
        db_feed = FeedEntity(id=id, **feed.dict())
        db.add(db_feed)
    db.commit()
    db.refresh(db_feed)
    return db_feed
