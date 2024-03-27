from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import relationship

from db.tables.base import Base


class FeedEntity(Base):
    __tablename__ = "feed"
    __table_args__ = {"schema": "news"}

    id = Column(BigInteger, primary_key=True, server_default=func.id_gen())
    url = Column(String, nullable=False, index=True)
    url_hash = Column(String, nullable=False, unique=True, index=True)
    publisher_id = Column(
        BigInteger, ForeignKey("publisher.id"), nullable=False, index=True
    )
    category = Column(String, nullable=False)
    enabled = Column(Boolean, default=True)
    created = Column(DateTime, server_default=func.now())
    modified = Column(DateTime, server_onupdate=func.now(), server_default=func.now())
    og_images = Column(Boolean, nullable=False, default=False)
    max_entries = Column(Integer, nullable=False, default=20)

    # define relationships
    publisher = relationship("PublisherEntity", back_populates="feeds")
    locales = relationship("FeedLocaleEntity", back_populates="feed")
    articles = relationship("ArticleEntity", back_populates="feed")
    update_records = relationship("FeedUpdateRecordEntity", back_populates="feed")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "url": self.url,
            "url_hash": self.url_hash,
            "publisher_id": self.publisher_id,
            "category": self.category,
            "enabled": self.enabled,
            "created": self.created,
            "modified": self.modified,
        }

    def to_insert(self) -> dict:
        return {
            "url": self.url,
            "url_hash": self.url_hash,
            "publisher_id": self.publisher_id,
            "category": self.category,
            "enabled": self.enabled,
        }

    def __str__(self):
        return f"<FeedEntity(id={self.id}, url={self.url}, publisher_id={self.publisher_id}, category={self.category})>"
