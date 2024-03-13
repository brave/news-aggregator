from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, func

from db.tables.base import Base


class FeedArticle(Base):
    __tablename__ = "feed_articles"
    __table_args__ = {"schema": "news"}
    id = Column(BigInteger, primary_key=True, server_default=func.id_gen())
    feed_id = Column(BigInteger, ForeignKey("feeds.id"), nullable=False, index=True)
    article_id = Column(
        BigInteger, ForeignKey("articles.id"), nullable=False, index=True
    )
    created = Column(DateTime(timezone=True), server_default=func.now())
    modified = Column(
        DateTime(timezone=True), server_onupdate=func.now(), server_default=func.now()
    )

    def __repr__(self) -> dict:
        return {
            "id": self.id,
            "feed_id": self.feed_id,
            "article_id": self.article_id,
            "created": self.created,
            "modified": self.modified,
        }

    def __str__(self) -> str:
        return f"FeedArticle id={self.id} feed_id={self.feed_id} article_id={self.article_id}"
