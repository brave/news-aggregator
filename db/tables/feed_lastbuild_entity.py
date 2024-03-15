from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, func

from db.tables.base import Base


class FeedLastBuild(Base):
    __tablename__ = "feed_lastbuild"
    __table_args__ = {"schema": "news"}

    id = Column(BigInteger, primary_key=True, server_default=func.id_gen())
    feed_id = Column(
        BigInteger, ForeignKey("feeds.id"), nullable=False, unique=True, index=True
    )
    last_build_timedate = Column(DateTime(timezone=True), nullable=False)
    last_build_timedelta = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    created = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    modified = Column(
        DateTime(timezone=True),
        server_onupdate=func.now(),
        server_default=func.now(),
        nullable=False,
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "feed_id": self.feed_id,
            "last_build_timedate": self.last_build_timedate,
            "last_build_timedelta": self.last_build_timedelta,
            "created": self.created,
            "modified": self.modified,
        }

    def __str__(self) -> str:
        return (
            f"FeedLastBuild id={self.id} feed_id={self.feed_id} "
            f"last_build_timedate={self.last_build_timedate} "
            f"last_build_timedelta={self.last_build_timedelta}"
        )
