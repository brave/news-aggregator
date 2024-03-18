import orjson
from sqlalchemy.dialects.postgresql import insert

from config import get_config
from db.tables.channel_entity import ChannelEntity
from db.tables.feed_entity import FeedEntity
from db.tables.locales_channels_entity import LocaleChannelEntity
from db.tables.locales_entity import LocaleEntity
from db.tables.publsiher_entity import PublisherEntity

config = get_config()


def insert_publisher(session, publisher):
    """
    Insert a new publisher into the database
    """
    # Create a new publisher entity
    new_publisher = PublisherEntity(
        name=publisher["name"],
        url=publisher["url"],
        favicon_url=publisher["favicon_url"],
        cover_url=publisher["cover_url"],
        background_color=publisher["background_color"],
        enabled=publisher["enabled"],
        score=publisher["score"],
    )
    session.execute(
        insert(PublisherEntity)
        .values(new_publisher.to_insert())
        .on_conflict_do_nothing()
    )
    return new_publisher


def insert_locale(session, locale):
    """
    Insert a new locale into the database
    """
    # Create a new locale entity
    new_locale = LocaleEntity(
        locale=locale["locale"],
        name=locale["locale"],
    )
    session.execute(
        insert(LocaleEntity).values(new_locale.to_insert()).on_conflict_do_nothing()
    )
    return new_locale


def insert_channel(session, channel):
    """
    Insert a new channel into the database
    """
    # Create a new channel entity
    new_channel = ChannelEntity(
        name=channel["channel"],
    )
    session.execute(
        insert(ChannelEntity).values(new_channel.to_insert()).on_conflict_do_nothing()
    )
    return new_channel


def insert_locale_channel(session, locale_id, channel_id):
    """
    Insert a new locale_channel into the database
    """
    # Create a new locale_channel entity
    new_locale_channel = LocaleChannelEntity(
        locale_id=locale_id,
        channel_id=channel_id,
    )
    session.execute(
        insert(LocaleChannelEntity)
        .values(new_locale_channel.to_insert())
        .on_conflict_do_nothing()
    )
    return new_locale_channel


def insert_feed(session, url, url_hash, category, enabled, locale_id, publisher_id):
    """
    Insert a new feed into the database
    """
    # Create a new feed entity
    new_feed = FeedEntity(
        url=url,
        url_hash=url_hash,
        publisher_id=publisher_id,
        category=category,
        enabled=enabled,
        locale_id=locale_id,
    )
    session.execute(
        insert(FeedEntity).values(new_feed.to_insert()).on_conflict_do_nothing()
    )
    return new_feed


if __name__ == "__main__":
    with config.get_db_session().begin() as db_session:
        with open(f"{config.output_path / config.global_sources_file}") as f:
            publishers_data_as_list = orjson.loads(f.read())

            for publisher_data in publishers_data_as_list:
                insert_publisher(db_session, publishers_data_as_list)
