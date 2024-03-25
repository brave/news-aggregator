from sqlalchemy import BigInteger, Column, ForeignKey, MetaData, Table
from sqlalchemy.ext.declarative import declarative_base

from config import get_config

config = get_config()

metadata_obj = MetaData(schema=config.schema_name)

Base = declarative_base(metadata=metadata_obj)

feed_locale_channel = Table(
    "feed_locale_channel",
    Base.metadata,
    Column("feed_locale_id", BigInteger, ForeignKey("feed_locale.id")),
    Column("channel_id", BigInteger, ForeignKey("channel.id")),
    schema=config.schema_name,
)

feed_article_association = Table(
    "feed_article",
    Base.metadata,
    Column("feed_id", BigInteger, ForeignKey("feed.id")),
    Column("article_id", BigInteger, ForeignKey("article.id")),
)
