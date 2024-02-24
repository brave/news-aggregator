import json
import shutil

import orjson
import structlog

from aggregator.aggregate import Aggregator
from config import get_config
from utils import upload_file

config = get_config()
logger = structlog.getLogger(__name__)

if __name__ == "__main__":
    feed_sources = config.output_path / config.feed_sources_path

    with open(feed_sources) as f:
        publishers = orjson.loads(f.read())
        output_path = config.output_feed_path / f"{config.feed_path}.json-tmp"

    fp = Aggregator(publishers, output_path)
    fp.aggregate()
    shutil.copyfile(
        config.output_feed_path / f"{config.feed_path}.json-tmp",
        config.output_feed_path / f"{config.feed_path}.json",
    )

    if not config.no_upload:
        upload_file(
            config.output_feed_path / f"{config.feed_path}.json",
            config.pub_s3_bucket,
            f"brave-today/{config.feed_path}{str(config.sources_file).replace('sources', '')}.json",
        )
        # Temporarily upload also with incorrect filename as a stopgap for
        # https://github.com/brave/brave-browser/issues/20114
        # Can be removed once fixed in the brave-core client for all Desktop users.
        upload_file(
            config.output_feed_path / f"{config.feed_path}.json",
            config.pub_s3_bucket,
            f"brave-today/{config.feed_path}{str(config.sources_file).replace('sources', '')}json",
        )
    with open(config.output_path / "report.json", "w") as f:
        f.write(json.dumps(fp.report))
