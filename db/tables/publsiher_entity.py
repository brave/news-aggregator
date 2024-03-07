from sqlalchemy import BigInteger, Boolean, Column, DateTime, Float, String, func

from db.tables.base import Base


class PublisherEntity(Base):
    __tablename__ = "publishers"
    __table_args__ = {"schema": "news"}

    id = Column(BigInteger, primary_key=True, server_default=func.id_gen())
    name = Column(String, nullable=False)
    url = Column(String, nullable=False, unique=True)
    favicon = Column(String, server_default="", nullable=True)
    cover_image = Column(String, server_default="", nullable=True)
    background_color = Column(String, server_default="", nullable=True)
    enabled = Column(Boolean, default=True)
    score = Column(Float, default=0.0, nullable=False)
    url_hash = Column(String, nullable=False, unique=True)
    created = Column(DateTime(timezone=True), server_default=func.now())
    modified = Column(
        DateTime(timezone=True), server_onupdate=func.now(), server_default=func.now()
    )

    def __repr__(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "url": self.url,
            "favicon": self.favicon,
            "cover_image": self.cover_image,
            "background_color": self.background_color,
            "enabled": self.enabled,
            "score": self.score,
            "url_hash": self.url_hash,
            "created": self.created,
            "modified": self.modified,
        }

    def __str__(self) -> str:
        return f"<PublisherEntity(id={self.id}, name={self.name}, url={self.url})>"
