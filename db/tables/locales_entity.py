from sqlalchemy import BigInteger, Column, DateTime, String, func

from db.tables.base import Base


class LocaleEntity(Base):
    __tablename__ = "locale"
    __table_args__ = {"schema": "news"}

    id = Column(BigInteger, primary_key=True, server_default=func.id_gen())
    name = Column(String, nullable=False)
    locale = Column(String(2), nullable=False, unique=True, index=True)
    created = Column(DateTime(timezone=True), server_default=func.now())
    modified = Column(
        DateTime(timezone=True), server_onupdate=func.now(), server_default=func.now()
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "locale": self.locale,
            "created": self.created,
            "modified": self.modified,
        }

    def to_insert(self) -> dict:
        return {
            "name": self.name,
            "locale": self.locale,
        }

    def __str__(self) -> str:
        return f"<LocaleEntity(id={self.id}, name={self.name}, locale={self.locale})>"
