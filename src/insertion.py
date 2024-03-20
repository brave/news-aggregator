import json

import orjson
import structlog

from config import get_config
from db.tables.channel_entity import ChannelEntity
from db.tables.feed_entity import FeedEntity
from db.tables.feed_locale_channel_entity import FeedLocaleChannelEntity
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


def insert_or_get_locale_channels(session, locale):
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


def insert_feed_locale_channel(session, feed_locale_id, channel_id):
    """
    Insert a new feed_locale_channel into the database
    """
    try:
        new_feed_locale_channel = FeedLocaleChannelEntity(
            feed_locale_id=feed_locale_id,
            channel_id=channel_id,
        )
        session.add(new_feed_locale_channel)
        session.commit()
        session.refresh(new_feed_locale_channel)
        return new_feed_locale_channel
    except Exception as e:
        logger.error(e)
        session.rollback()


def get_publisher(session, publisher_url: str):
    """
    Get a publisher from the database
    """

    publisher = session.query(PublisherEntity).filter_by(url=publisher_url).first()

    publisher_info = {
        "enabled": publisher.feeds[0].enabled,
        "publisher_name": publisher.name,
        "category": publisher.feeds[0].category,
        "site_url": publisher.url,
        "feed_url": publisher.feeds[0].url,
        "favicon_url": publisher.favicon_url,
        "cover_url": publisher.cover_url,
        "background_color": publisher.background_color,
        "score": publisher.score,
        "publisher_id": publisher.feeds[0].url_hash,
        "locales": [],
    }

    for feed in publisher.feeds:
        for feed_locale in feed.locales:
            locale_data = {
                "locale": feed_locale.locale.locale,
                "channels": [channel.channel_name for channel in feed_locale.channels],
                "rank": feed_locale.rank,
            }
            publisher_info["locales"].append(locale_data)

    json_result = json.dumps([publisher_info], indent=4)
    print(json_result)


if __name__ == "__main__":
    with config.get_db_session() as db_session:
        publisher = get_publisher(db_session, "https://www.andpremium.jp")
        with open(f"{config.output_path / config.global_sources_file}") as f:
            try:
                publishers_data_as_list = orjson.loads(f.read())

                for publisher_data in publishers_data_as_list:
                    print("=========================================================")
                    print(publisher_data)
                    print("=========================================================")
                    publisher = insert_or_get_publisher(db_session, publisher_data)
                    feed = insert_or_get_feed(
                        db_session,
                        publisher_data,
                        publisher_id=publisher.id,
                    )
                    for locale_data in publisher_data["locales"]:
                        locale = insert_or_get_locale_channels(
                            db_session, locale_data["locale"]
                        )

                        # Insert the feed_locale_channel
                        feed_locale = insert_feed_locale(
                            db_session, feed.id, locale.id, locale_data["rank"]
                        )

                        channels = locale_data["channels"]
                        if channels:
                            for channel in channels:
                                new_channel = insert_or_get_channel(db_session, channel)
                                feed_locale_channel = insert_feed_locale_channel(
                                    db_session, feed_locale.id, new_channel.id
                                )

                    1 == 1

            except Exception as e:
                logger.error(e)
