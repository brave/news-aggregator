from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status

from api.utils import ep_err_msg, request_auth

router = APIRouter(
    responses={status.HTTP_404_NOT_FOUND: {"Description": ep_err_msg}},
    dependencies=[Depends(request_auth)],
)


@router.get("/api/articles", response_model=List[dict])
async def get_articles_with_locale(
    start_date: datetime = Query(..., description="Start date for the articles"),
    end_date: Optional[datetime] = Query(None, description="End date for the articles"),
    locale: Optional[str] = Query(None, description="Locale for the articles"),
    cache_hits: Optional[bool] = Query(
        None, description="Filter articles based on cache hits"
    ),
    external_channels: Optional[bool] = Query(
        None, description="Filter articles from external channels"
    ),
):
    articles = None
    return articles
