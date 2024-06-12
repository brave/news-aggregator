from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from api.utils import ep_err_msg, get_db, request_auth
from db.tables.channel_entity import ChannelEntity

router = APIRouter(
    responses={status.HTTP_404_NOT_FOUND: {"Description": ep_err_msg}},
    dependencies=[Depends(request_auth)],
)


class ChannelBase(BaseModel):
    name: str


class ChannelCreate(ChannelBase):
    pass


class Channel(ChannelBase):
    id: int
    created: datetime
    modified: datetime

    class Config:
        from_attributes = True


@router.get("/api/channels", response_model=List[Channel])
async def get_channels_from_db(db: Session = Depends(get_db)):
    channels = db.query(ChannelEntity.name).distinct().all()
    return channels


@router.post("/api/channels", response_model=Channel)
async def create_channel(channel: ChannelCreate, db: Session = Depends(get_db)):
    db_channel = (
        db.query(ChannelEntity).filter(ChannelEntity.name == channel.name).first()
    )
    if db_channel:
        raise HTTPException(status_code=400, detail="Channel already exists")
    db_channel = ChannelEntity(**channel.dict())
    db.add(db_channel)
    db.commit()
    db.refresh(db_channel)
    return db_channel


@router.put("/api/channels/{id}", response_model=Channel)
async def update_channel(
    id: int, channel: ChannelCreate, db: Session = Depends(get_db)
):
    db_channel = db.query(ChannelEntity).filter(ChannelEntity.id == id).first()
    if db_channel is None:
        raise HTTPException(status_code=404, detail="Channel not found")
    for key, value in channel.dict().items():
        setattr(db_channel, key, value)
    db.commit()
    db.refresh(db_channel)
    return db_channel
