import re

from sqlalchemy import BigInteger, Column, ForeignKey, MetaData, Table
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import CreateTable

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


@compiles(CreateTable)
def _add_if_not_exists(element, compiler, **kw):
    output = compiler.visit_create_table(element, **kw)
    if element.element.info.get("ifexists"):
        output = re.sub("^\\s*CREATE TABLE", "CREATE TABLE IF NOT EXISTS", output, re.S)
    return output
