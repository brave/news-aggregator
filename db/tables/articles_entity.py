from sqlalchemy import BigInteger, Column, DateTime, Float, ForeignKey, String, func
from sqlalchemy.orm import relationship

from db.tables.base import Base


class ArticleEntity(Base):
    __tablename__ = "article"
    __table_args__ = {"schema": "news"}

    id = Column(BigInteger, primary_key=True, server_default=func.id_gen())
    title = Column(String, nullable=False)
    publish_time = Column(DateTime, nullable=False)
    img = Column(String, default="", nullable=False)
    category = Column(String, nullable=False)
    description = Column(String, nullable=True)
    content_type = Column(String, nullable=False, default="article")
    creative_instance_id = Column(String, default="", nullable=False)
    url = Column(String, nullable=False)
    url_hash = Column(String, nullable=False, unique=True, index=True)
    pop_score = Column(Float, default=0.0, nullable=False)
    padded_img = Column(String, default="", nullable=False)
    score = Column(Float, default=0.0, nullable=False)
    created = Column(DateTime, nullable=False, server_default=func.now())
    modified = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    feed_id = Column(BigInteger, ForeignKey("feed.id"), nullable=False, index=True)

    feed = relationship("FeedEntity", back_populates="articles")

    cache_record = relationship("ArticleCacheRecordEntity", back_populates="article")

    classification = relationship(
        "ArticleClassificationEntity", back_populates="article"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "publish_time": self.publish_time,
            "img_url": self.img,
            "category": self.category,
            "description": self.description,
            "content_type": self.content_type,
            "creative_instance_id": self.creative_instance_id,
            "url": self.url,
            "url_hash": self.url_hash,
            "pop_score": self.pop_score,
            "padded_img_url": self.padded_img,
            "score": self.score,
            "created": self.created,
            "modified": self.modified,
        }

    def to_insert(self) -> dict:
        return {
            "title": self.title,
            "publish_time": self.publish_time,
            "img_url": self.img,
            "category": self.category,
            "description": self.description,
            "content_type": self.content_type,
            "creative_instance_id": self.creative_instance_id,
            "url": self.url,
            "url_hash": self.url_hash,
            "pop_score": self.pop_score,
            "padded_img_url": self.padded_img,
            "score": self.score,
        }

    def __str__(self):
        return f"<ArticleEntity(id={self.id}, title={self.title}, url={self.url})>"
