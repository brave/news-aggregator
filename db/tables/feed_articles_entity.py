from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, func

from db.tables.base import Base


class FeedArticleEntity(Base):
    __tablename__ = "feed_article"
    __table_args__ = {"schema": "news"}
    id = Column(BigInteger, primary_key=True, server_default=func.id_gen())
    feed_id = Column(BigInteger, ForeignKey("feed.id"), nullable=False, index=True)
    article_id = Column(
        BigInteger, ForeignKey("article.id"), nullable=False, index=True
    )
    created = Column(DateTime, server_default=func.now())
    modified = Column(DateTime, server_onupdate=func.now(), server_default=func.now())

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "feed_id": self.feed_id,
            "article_id": self.article_id,
            "created": self.created,
            "modified": self.modified,
        }

    def to_insert(self) -> dict:
        return {
            "feed_id": self.feed_id,
            "article_id": self.article_id,
        }

    def __str__(self) -> str:
        return f"FeedArticle id={self.id} feed_id={self.feed_id} article_id={self.article_id}"
