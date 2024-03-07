from sqlalchemy import BigInteger, Column, DateTime, String, func

from db.tables.base import Base


class ChannelEntity(Base):
    __tablename__ = "channels"
    __table_args__ = {"schema": "news"}

    id = Column(BigInteger, primary_key=True, server_default=func.id_gen())
    name = Column(String, nullable=False, unique=True)
    created = Column(DateTime(timezone=True), server_default=func.now())
    modified = Column(
        DateTime(timezone=True), server_onupdate=func.now(), server_default=func.now()
    )

    def __repr__(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "created": self.created,
            "modified": self.modified,
        }

    def __str__(self):
        return f"channel_entity(id={self.id!r}, name={self.name!r})"
