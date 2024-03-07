from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer, func

from db.tables.base import Base


class FeedLocaleEntity(Base):
    __tablename__ = "feed_locales"
    __table_args__ = {"schema": "news"}

    id = Column(BigInteger, primary_key=True, server_default=func.id_gen())
    feed_id = Column(BigInteger, ForeignKey("feeds.id"), nullable=False)
    locale_id = Column(BigInteger, ForeignKey("locales.id"), nullable=False)
    rank = Column(Integer, nullable=False)
    created = Column(DateTime(timezone=True), server_default=func.now())
    modified = Column(
        DateTime(timezone=True), server_onupdate=func.now(), server_default=func.now()
    )

    def __repr__(self) -> dict:
        return {
            "id": self.id,
            "feed_id": self.feed_id,
            "locale_id": self.locale_id,
            "rank": self.rank,
            "created": self.created,
            "modified": self.modified,
        }

    def __str__(self) -> str:
        return f"<FeedLocaleEntity(id={self.id}, feed_id={self.feed_id}, locale_id={self.locale_id}, rank={self.rank})>"
