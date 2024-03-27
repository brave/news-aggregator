from sqlalchemy import BigInteger, Boolean, Column, DateTime, Float, String, func
from sqlalchemy.orm import relationship

from db.tables.base import Base


class PublisherEntity(Base):
    __tablename__ = "publisher"
    __table_args__ = {"schema": "news"}

    id = Column(BigInteger, primary_key=True, server_default=func.id_gen())
    name = Column(String, nullable=False)
    url = Column(String, nullable=False, unique=True, index=True)
    favicon_url = Column(String, server_default=None, nullable=True)
    cover_url = Column(String, server_default=None, nullable=True)
    background_color = Column(String, server_default=None, nullable=True)
    enabled = Column(Boolean, default=True)
    score = Column(Float, default=0.0, nullable=False)
    created = Column(DateTime, server_default=func.now())
    modified = Column(DateTime, server_onupdate=func.now(), server_default=func.now())

    feeds = relationship("FeedEntity", back_populates="publisher")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "url": self.url,
            "favicon_url": self.favicon_url,
            "cover_url": self.cover_url,
            "background_color": self.background_color,
            "enabled": self.enabled,
            "score": self.score,
            "created": self.created,
            "modified": self.modified,
        }

    def to_insert(self) -> dict:
        return {
            "name": self.name,
            "url": self.url,
            "favicon_url": self.favicon_url,
            "cover_url": self.cover_url,
            "background_color": self.background_color,
            "enabled": self.enabled,
            "score": self.score,
        }

    def __str__(self) -> str:
        return f"<PublisherEntity(id={self.id}, name={self.name}, url={self.url})>"
