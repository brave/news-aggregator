from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from api.utils import ep_err_msg, get_db, request_auth
from db.tables.article_cache_record_entity import ArticleCacheRecordEntity
from db.tables.articles_entity import ArticleEntity
from db.tables.external_article_classification_entity import (
    ExternalArticleClassificationEntity,
)
from db.tables.locales_entity import LocaleEntity

router = APIRouter(
    responses={status.HTTP_404_NOT_FOUND: {"Description": ep_err_msg}},
    dependencies=[Depends(request_auth)],
)


class ArticleBase(BaseModel):
    title: str
    publish_time: datetime
    img: str
    category: str
    description: Optional[str]
    content_type: str
    creative_instance_id: str
    url: str
    url_hash: str
    pop_score: float
    padded_img: str
    score: float


class Article(ArticleBase):
    id: int
    created: datetime
    modified: datetime

    class Config:
        from_attributes = True


@router.get("/api/articles", response_model=List[Article])
async def get_articles(
    start_date: datetime = Query(..., description="Start date for the articles"),
    end_date: Optional[datetime] = Query(None, description="End date for the articles"),
    locale: Optional[str] = Query(None, description="Locale for the articles"),
    cache_hits: Optional[bool] = Query(
        None, description="Filter articles based on cache hits"
    ),
    external_channels: Optional[bool] = Query(
        None, description="Filter articles from external channels"
    ),
    db: Session = Depends(get_db),
):
    query = (
        db.query(ArticleEntity)
        .join(ArticleCacheRecordEntity)
        .join(LocaleEntity, isouter=True)
        .join(ExternalArticleClassificationEntity, isouter=True)
    )

    query = query.filter(ArticleEntity.publish_time >= start_date)

    if end_date:
        query = query.filter(ArticleEntity.publish_time <= end_date)

    if locale:
        query = query.filter(LocaleEntity.locale == locale)

    if cache_hits is not None:
        query = query.filter(
            ArticleCacheRecordEntity.cache_hit > 0
            if cache_hits
            else ArticleCacheRecordEntity.cache_hit == 0
        )

    if external_channels is not None:
        if external_channels:
            query = query.filter(
                ExternalArticleClassificationEntity.channels.isnot(None)
            )
        else:
            query = query.filter(ExternalArticleClassificationEntity.channels.is_(None))

    articles = query.all()
    return articles
