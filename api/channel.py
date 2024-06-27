from typing import List

from fastapi import APIRouter, Depends, status

from api.utils import ep_err_msg, request_auth
from db_crud import get_channels

router = APIRouter(
    responses={status.HTTP_404_NOT_FOUND: {"Description": ep_err_msg}},
    dependencies=[Depends(request_auth)],
)


@router.get("/api/channels", response_model=List)
async def get_channels_from_db():
    channels = get_channels()
    return channels
