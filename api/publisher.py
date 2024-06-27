import re
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel

from api.utils import ep_err_msg, request_auth
from db_crud import get_feeds_based_on_locale, get_publisher_with_locale

router = APIRouter(
    responses={status.HTTP_404_NOT_FOUND: {"Description": ep_err_msg}},
    dependencies=[Depends(request_auth)],
)


@router.post("/api/publisher", response_model=List[dict])
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


class PublisherRequest(BaseModel):
    locale: str
    publisher_blocklist: List[str]
    channels_to_include: List[str]


@router.post("/api/publisher_with_locale/ids", response_model=List[dict])
async def read_publisher_id_with_locale(request: PublisherRequest):
    locale = request.locale
    if not re.match(r"[a-z]{2}_[A-Z]{2}", locale) or len(locale) != 5:
        raise ValueError(
            "Locale must be in the format 'xx_XX' and exactly 5 characters long."
        )

    publisher_blocklist = request.publisher_blocklist
    channels_to_include = request.channels_to_include

    relevant_publishers = []
    publishers = get_feeds_based_on_locale(locale)
    for source in publishers:
        if source["publisher_name"] in publisher_blocklist:
            continue

        if source["channels"] and not set(channels_to_include).isdisjoint(
            source["channels"]
        ):
            relevant_publishers.append(source["publisher_id"])

    return relevant_publishers
