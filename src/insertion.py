import orjson
import structlog

from config import get_config
from db.tables.channel_entity import ChannelEntity
from db.tables.feed_entity import FeedEntity
from db.tables.feed_locales_entity import FeedLocaleEntity
from db.tables.locale_channel_entity import LocaleChannelEntity
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


def insert_locale_channels(session, locales_channels):
    """
    Insert a new locale into the database
    """
    locale, channels = locales_channels["locale"], locales_channels["channels"]
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

    if channels:
        for channel in channels:
            new_channel = insert_channel(session, channel)
            try:
                new_locale_channel = LocaleChannelEntity(
                    locale_id=new_locale.id,
                    channel_id=new_channel.id,
                )
                session.add(new_locale_channel)
                session.commit()
                session.refresh(new_locale_channel)

            except Exception as e:
                logger.error(e)
                session.rollback()

    return new_locale


def insert_channel(session, channel):
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


if __name__ == "__main__":
    with config.get_db_session() as db_session:
        with open(f"{config.output_path / config.global_sources_file}") as f:
            try:
                publishers_data_as_list = orjson.loads(f.read())
                publishers_data_as_list = [
                    {
                        "enabled": True,
                        "publisher_name": "Business Insider",
                        "category": "Business",
                        "site_url": "https://www.businessinsider.com",
                        "feed_url": "https://feeds.businessinsider.com/custom/all",
                        "favicon_url": None,
                        "cover_url": None,
                        "background_color": None,
                        "score": 0.0,
                        "destination_domains": [
                            "markets.businessinsider.com",
                            "www.businessinsider.com",
                            "www.insiderintelligence.com",
                        ],
                        "publisher_id": "94894689757967eabb4fce2d04eabe3387efc0da9881b2c31d5fb77201f999e1",
                        "locales": [
                            {
                                "locale": "en_CA",
                                "channels": ["Business", "Top Sources"],
                                "rank": 22,
                            },
                            {
                                "locale": "en_US",
                                "channels": ["Business", "Top Sources"],
                                "rank": 17,
                            },
                            {
                                "locale": "en_GB",
                                "channels": ["Business", "Top Sources"],
                                "rank": 27,
                            },
                        ],
                    }
                ]

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
                        locale = insert_locale_channels(db_session, locale_data)

                        # Insert the feed_locale_channel
                        feed_locale = insert_feed_locale(
                            db_session, feed.id, locale.id, locale_data["rank"]
                        )

            except Exception as e:
                logger.error(e)
