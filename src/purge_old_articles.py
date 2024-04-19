import structlog

from config import get_config
from db_crud import delete_old_articles

config = get_config()
logger = structlog.getLogger(__name__)


if __name__ == "__main__":
    delete_old_articles()
    logger.info("Old articles deleted.")
