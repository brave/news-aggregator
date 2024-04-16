from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, String, func

from db.tables.base import Base


class ArticleCacheRecordEntity(Base):
    __tablename__ = "article_cache_record_entity"

    id = Column(BigInteger, primary_key=True, server_default=func.id_gen())
    article_id = Column(
        BigInteger, ForeignKey("article.id"), nullable=False, index=True
    )
    cache_hit = Column(String, nullable=False)
    created = Column(DateTime, nullable=False, server_default=func.now())
    modified = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "article_id": self.article_id,
            "content": self.cache_hit,
            "created": self.created,
            "modified": self.modified,
        }

    def to_insert(self) -> dict:
        return {
            "article_id": self.article_id,
            "content": self.cache_hit,
        }

    def __str__(self):
        return str(self.id)
