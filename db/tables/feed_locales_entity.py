from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer, func

from db.tables.base import Base
from db.tables.feed_entity import FeedEntity
from db.tables.locales_entity import LocaleEntity


class FeedLocaleEntity(Base):
    __tablename__ = "feed_locale"
    __table_args__ = {"schema": "news"}

    id = Column(BigInteger, primary_key=True, server_default=func.id_gen())
    feed_id = Column(BigInteger, ForeignKey(FeedEntity.id), nullable=False, index=True)
    locale_id = Column(
        BigInteger, ForeignKey(LocaleEntity.id), nullable=False, index=True
    )
    rank = Column(Integer, nullable=False)
    created = Column(DateTime(timezone=True), server_default=func.now())
    modified = Column(
        DateTime(timezone=True), server_onupdate=func.now(), server_default=func.now()
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "feed_id": self.feed_id,
            "locale_id": self.locale_id,
            "rank": self.rank,
            "created": self.created,
            "modified": self.modified,
        }

    def to_insert(self) -> dict:
        return {
            "feed_id": self.feed_id,
            "locale_id": self.locale_id,
            "rank": self.rank,
        }

    def __str__(self) -> str:
        return f"<FeedLocaleEntity(id={self.id}, feed_id={self.feed_id}, locale_id={self.locale_id}, rank={self.rank})>"
