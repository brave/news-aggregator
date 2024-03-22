from copy import deepcopy

import orjson
import structlog

from config import get_config
from db.tables.base import feed_locale_channel
from db.tables.channel_entity import ChannelEntity
from db.tables.feed_entity import FeedEntity
from db.tables.feed_locales_entity import FeedLocaleEntity
from db.tables.locales_entity import LocaleEntity
from db.tables.publsiher_entity import PublisherEntity

config = get_config()
logger = structlog.getLogger(__name__)


def insert_or_get_publisher(session, publisher):
    """
    Insert a new publisher into the database
    """
    try:
        # Create a new publisher entity
        new_publisher = PublisherEntity(
            name=publisher["publisher_name"],
            url=publisher["site_url"],
            favicon_url=publisher["favicon_url"],
            cover_url=publisher["cover_url"],
            background_color=publisher["background_color"],
            enabled=publisher["enabled"],
            score=publisher["score"],
        )
        session.add(new_publisher)
        session.commit()
        session.refresh(new_publisher)
        return new_publisher
    except Exception as e:
        logger.error(e)
        session.rollback()
        return (
            session.query(PublisherEntity).filter_by(url=publisher["site_url"]).first()
        )


def insert_or_get_locale(session, locale):
    """
    Insert a new locale into the database
    """
    try:
        # Create a new locale entity
        new_locale = LocaleEntity(
            locale=locale,
            name=locale,
        )
        session.add(new_locale)
        session.commit()
        session.refresh(new_locale)

    except Exception as e:
        logger.error(e)
        session.rollback()
        new_locale = session.query(LocaleEntity).filter_by(locale=locale).first()

    return new_locale


def insert_or_get_channel(session, channel):
    """
    Insert a new channel into the database
    """
    try:
        new_channel = ChannelEntity(
            name=channel,
        )
        session.add(new_channel)
        session.commit()
        session.refresh(new_channel)
        return new_channel
    except Exception as e:
        logger.error(e)
        session.rollback()
        return session.query(ChannelEntity).filter_by(name=channel).first()


def insert_or_get_feed(session, feed_data, publisher_id):
    """
    Insert a new feed into the database
    """
    try:
        new_feed = FeedEntity(
            url=feed_data["feed_url"],
            url_hash=feed_data["publisher_id"],
            publisher_id=publisher_id,
            category=feed_data["category"],
            enabled=feed_data["enabled"],
        )
        session.add(new_feed)
        session.commit()
        session.refresh(new_feed)
        return new_feed
    except Exception as e:
        logger.error(e)
        session.rollback()
        return (
            session.query(FeedEntity)
            .filter_by(url_hash=feed_data["publisher_id"])
            .first()
        )


def insert_feed_locale(session, feed_id, locale_id, rank):
    """
    Insert a new feed_locale_channel into the database
    """
    try:
        new_feed_locale = FeedLocaleEntity(
            feed_id=feed_id,
            locale_id=locale_id,
            rank=rank,
        )
        session.add(new_feed_locale)
        session.commit()
        session.refresh(new_feed_locale)
        return new_feed_locale
    except Exception as e:
        logger.error(e)
        session.rollback()


def insert_or_update_all_publishers(db_session):
    """
    Insert or update all publishers in the database
    """
    with open(f"{config.output_path / config.global_sources_file}") as f:
        try:
            logger.info("Inserting publisher data")

            publishers_data_as_list = orjson.loads(f.read())
            publishers_data_as_list = publishers_data_as_list
            for publisher_data in publishers_data_as_list:
                publisher = insert_or_get_publisher(db_session, publisher_data)

                feed = insert_or_get_feed(
                    db_session,
                    publisher_data,
                    publisher_id=publisher.id,
                )

                for locale_item in publisher_data["locales"]:
                    locale = insert_or_get_locale(db_session, locale_item["locale"])

                    feed_locale = insert_feed_locale(
                        db_session, feed.id, locale.id, locale_item["rank"]
                    )

                    for channel_name in locale_item["channels"]:
                        channel = insert_or_get_channel(db_session, channel_name)

                        try:
                            feed_locale.channels.append(channel)
                            db_session.commit()
                        except Exception:
                            logger.error(
                                f"Channels data already inserted for {publisher.url}"
                            )

            logger.info("Publisher data inserted successfully")

        except Exception as e:
            logger.error(e)


def get_publisher(session, publisher_url: str):
    """
    Get a publisher from the database
    """

    data = []
    publisher = session.query(PublisherEntity).filter_by(url=publisher_url).first()
    if publisher:
        publisher_data = {
            "enabled": publisher.enabled,
            "publisher_name": publisher.name,
            "site_url": publisher.url,
            "feed_url": "",
            "category": "",
            "favicon_url": publisher.favicon_url,
            "cover_url": publisher.cover_url,
            "background_color": publisher.background_color,
            "score": publisher.score,
            "publisher_id": "",
            "locales": [],
        }

        feeds = session.query(FeedEntity).filter_by(publisher_id=publisher.id).all()
        for feed in feeds:
            feed_publisher_data = deepcopy(publisher_data)
            feed_publisher_data["feed_url"] = feed.url
            feed_publisher_data["category"] = feed.category
            feed_publisher_data["enabled"] = feed.enabled
            feed_publisher_data["publisher_id"] = feed.url_hash

            feed_locales = (
                session.query(FeedLocaleEntity).filter_by(feed_id=feed.id).all()
            )
            for feed_locale in feed_locales:
                locale = (
                    session.query(LocaleEntity)
                    .filter_by(id=feed_locale.locale_id)
                    .first()
                )
                channels = (
                    session.query(ChannelEntity)
                    .join(feed_locale_channel)
                    .filter_by(feed_locale_id=feed_locale.id)
                    .all()
                )

                locale_data = {
                    "locale": locale.locale,
                    "channels": [channel.name for channel in channels],
                    "rank": feed_locale.rank,
                }
                feed_publisher_data["locales"].append(locale_data)

            data.append(feed_publisher_data)

    return data


if __name__ == "__main__":
    with config.get_db_session() as db_session:
        insert_or_update_all_publishers(db_session)
        # publisher = get_publisher(db_session, "https://www.businessinsider.com")
        # print(orjson.dumps(publisher).decode())
