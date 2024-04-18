from datetime import datetime, timedelta

import structlog

from config import get_config
from db.tables.articles_entity import ArticleEntity

config = get_config()
logger = structlog.getLogger(__name__)


def delete_old_articles():
    try:
        with config.get_db_session() as session:
            seven_days_ago = datetime.utcnow() - timedelta(days=7)
            session.query(ArticleEntity).filter(
                ArticleEntity.created < seven_days_ago
            ).delete()

            session.commit()
    except Exception as e:
        logger.error(e)


if __name__ == "__main__":
    delete_old_articles()
    logger.info("Old articles deleted.")
