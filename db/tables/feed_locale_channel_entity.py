from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, func

from db.tables.base import Base
from db.tables.channel_entity import ChannelEntity
from db.tables.feed_locales_entity import FeedLocaleEntity


class FeedLocaleChannelEntity(Base):
    __tablename__ = "feed_locale_channel"
    __table_args__ = {"schema": "news"}

    id = Column(BigInteger, primary_key=True, server_default=func.id_gen())
    feed_locale_id = Column(
        BigInteger, ForeignKey(FeedLocaleEntity.id), nullable=False, index=True
    )
    channel_id = Column(
        BigInteger, ForeignKey(ChannelEntity.id), nullable=False, index=True
    )
    created = Column(DateTime(timezone=True), server_default=func.now())
    modified = Column(
        DateTime(timezone=True), server_onupdate=func.now(), server_default=func.now()
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "feed_locale_id": self.locale,
            "channel_id": self.channel_id,
            "created": self.created,
            "modified": self.modified,
        }

    def to_insert(self) -> dict:
        return {
            "feed_locale_id": self.locale_id,
            "channel_id": self.channel_id,
        }

    def __str__(self):
        return f"feed_locale_id: {self.locale}, channel_id: {self.channel_id}"
