from typing import List

from fastapi import APIRouter, Depends, status

from api.utils import ep_err_msg, request_auth
from db_crud import get_locales

router = APIRouter(
    responses={status.HTTP_404_NOT_FOUND: {"Description": ep_err_msg}},
    dependencies=[Depends(request_auth)],
)


@router.get("/api/locales", response_model=List)
async def read_locales():
    locales = get_locales()
    return locales
