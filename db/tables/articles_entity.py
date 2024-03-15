from sqlalchemy import BigInteger, Column, DateTime, Float, String, func

from db.tables.base import Base


class ArticleEntity(Base):
    __tablename__ = "article"
    __table_args__ = {"schema": "news"}

    id = Column(BigInteger, primary_key=True, server_default=func.id_gen())
    title = Column(String, nullable=False)
    publish_time = Column(DateTime(True), nullable=False)
    img_url = Column(String, default="")
    category = Column(String, nullable=False)
    description = Column(String, nullable=True)
    content_type = Column(String, nullable=False, default="article")
    creative_instance_id = Column(String, default="")
    url = Column(String, nullable=False, unique=True, index=True)
    url_hash = Column(String, nullable=False, unique=True, index=True)
    pop_score = Column(Float, default=0.0, nullable=False)
    padded_img_url = Column(String, default="")
    score = Column(Float, default=0.0, nullable=False)
    created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    modified = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "publish_time": self.publish_time,
            "img_url": self.img_url,
            "category": self.category,
            "description": self.description,
            "content_type": self.content_type,
            "creative_instance_id": self.creative_instance_id,
            "url": self.url,
            "url_hash": self.url_hash,
            "pop_score": self.pop_score,
            "padded_img_url": self.padded_img_url,
            "score": self.score,
            "created": self.created,
            "modified": self.modified,
        }

    def __str__(self):
        return f"<ArticleEntity(id={self.id}, title={self.title}, url={self.url})>"
