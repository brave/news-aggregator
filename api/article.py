import re
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel

from api.utils import ep_err_msg, request_auth
from db_crud import get_articles_with_locale

router = APIRouter(
    responses={status.HTTP_404_NOT_FOUND: {"Description": ep_err_msg}},
    dependencies=[Depends(request_auth)],
)


@router.get("/api/articles", response_model=List[dict])
async def get_articles(
    start_datetime: datetime = Query(..., description="Start date for the articles"),
    end_datetime: Optional[datetime] = Query(
        None, description="End date for the articles"
    ),
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


class ArticleRequestCS(BaseModel):
    start_datetime: str = (datetime.utcnow() - timedelta(hours=2)).strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    locale: str


@router.post("/api/articles_with_locale", response_model=List[dict])
async def read_articles_with_locale(request: ArticleRequestCS):
    locale = request.locale
    if not re.match(r"[a-z]{2}_[A-Z]{2}", locale) or len(locale) != 5:
        raise ValueError(
            "Locale must be in the format 'xx_XX' and exactly 5 characters long."
        )

    articles = get_articles_with_locale(locale, request.start_datetime)
    return articles
