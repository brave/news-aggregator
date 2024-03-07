from sqlalchemy import BigInteger, Column, DateTime, String, func

from db.tables.base import Base


class LocaleEntity(Base):
    __tablename__ = "locales"
    __table_args__ = {"schema": "news"}

    id = Column(BigInteger, primary_key=True, server_default=func.id_gen())
    name = Column(String, nullable=False)
    locale = Column(String, nullable=False, unique=True)
    created = Column(DateTime(timezone=True), server_default=func.now())
    modified = Column(
        DateTime(timezone=True), server_onupdate=func.now(), server_default=func.now()
    )

    def __repr__(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "locale": self.locale,
            "created": self.created,
            "modified": self.modified,
        }

    def __str__(self) -> str:
        return f"<LocaleEntity(id={self.id}, name={self.name}, locale={self.locale})>"
