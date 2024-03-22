from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship

from db.tables.base import Base, feed_locale_channel


class FeedLocaleEntity(Base):
    __tablename__ = "feed_locale"
    __table_args__ = (UniqueConstraint("feed_id", "locale_id", "rank"),)

    id = Column(BigInteger, primary_key=True, server_default=func.id_gen())
    feed_id = Column(BigInteger, ForeignKey("feed.id"), nullable=False, index=True)
    locale_id = Column(BigInteger, ForeignKey("locale.id"), nullable=False, index=True)
    rank = Column(Integer, nullable=False, default=0)
    created = Column(DateTime(timezone=True), server_default=func.now())
    modified = Column(
        DateTime(timezone=True), server_onupdate=func.now(), server_default=func.now()
    )

    feed = relationship("FeedEntity", back_populates="locales")
    locale = relationship("LocaleEntity")
    channels = relationship("ChannelEntity", secondary=feed_locale_channel)

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
