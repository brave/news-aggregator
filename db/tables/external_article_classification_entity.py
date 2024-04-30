from sqlalchemy import ARRAY, BigInteger, Column, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from db.tables.base import Base


class ExternalArticleClassificationEntity(Base):
    __tablename__ = "external_article_classification"

    id = Column(BigInteger, primary_key=True, server_default=func.id_gen())
    article_id = Column(BigInteger, ForeignKey("external_article.id"))
    channels = Column(ARRAY(String), nullable=False)
    raw_data = Column(JSONB, nullable=True)
    created = Column(DateTime, nullable=False, server_default=func.now())
    modified = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    article = relationship("ExternalArticleEntity", back_populates="classification")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "article_id": self.article_id,
            "channels": self.channels,
            "created": self.created,
            "modified": self.modified,
        }

    def to_insert(self) -> dict:
        return {
            "article_id": self.article_id,
            "channels": self.channels,
        }

    def __str__(self) -> str:
        return f"ExternalArticleClassification id={self.id} article_id={self.article_id} channels={self.channels}"
