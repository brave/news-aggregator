from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status

from api.utils import ep_err_msg, request_auth
from db_crud import get_feeds_based_on_locale, get_publisher_with_locale

router = APIRouter(
    responses={status.HTTP_404_NOT_FOUND: {"Description": ep_err_msg}},
    dependencies=[Depends(request_auth)],
)


@router.get("/api/publisher", response_model=List[dict])
async def read_publisher(
    publisher_url: str = Query(..., description="Publisher URL"),
    locale: Optional[str] = Query(
        default=None,
        max_length=5,
        min_length=5,
        description="Locale information",
        regex="[a-z]{2}_[A-Z]{2}",
    ),
):
    publishers = get_publisher_with_locale(publisher_url, locale)
    return publishers


@router.get("/api/publisher_with_locale", response_model=List[dict])
async def read_publisher_with_locale(
    locale: str = Query(
        ...,
        max_length=5,
        min_length=5,
        description="Locale information",
        regex="[a-z]{2}_[A-Z]{2}",
    )
):
    publishers = get_feeds_based_on_locale(locale)
    return publishers
