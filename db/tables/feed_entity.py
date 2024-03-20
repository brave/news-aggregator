from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, String, func
from sqlalchemy.orm import relationship

from db.tables.base import Base
from db.tables.publsiher_entity import PublisherEntity


class FeedEntity(Base):
    __tablename__ = "feed"
    __table_args__ = {"schema": "news"}

    id = Column(BigInteger, primary_key=True, server_default=func.id_gen())
    url = Column(String, nullable=False, unique=True, index=True)
    url_hash = Column(String, nullable=False, unique=True, index=True)
    publisher_id = Column(
        BigInteger, ForeignKey(PublisherEntity.id), nullable=False, index=True
    )
    category = Column(String, nullable=False)
    enabled = Column(Boolean, default=True)
    created = Column(DateTime(timezone=True), server_default=func.now())
    modified = Column(
        DateTime(timezone=True), server_onupdate=func.now(), server_default=func.now()
    )

    # define relationships
    publisher = relationship("PublisherEntity", back_populates="feeds")
    locales = relationship(
        "FeedLocaleEntity", back_populates="feed"
    )  # Add back_populates here

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
