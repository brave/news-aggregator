import json
import math
import time
from datetime import datetime, timedelta, timezone

import pytz
import structlog
from sentry_sdk import capture_exception

from config import get_config
from utils import ExpiredRegions, s3_client, upload_file

logger = structlog.getLogger(__name__)
config = get_config()


def get_last_modified_date(bucket_name: str, file_key: str) -> datetime:
    try:
        response = s3_client.head_object(Bucket=bucket_name, Key=file_key)
        last_modified = response["LastModified"]
        return last_modified.astimezone(pytz.utc)
    except Exception as e:
        logger.error(f"Error retrieving last modified date for {file_key}: {e}")
        return datetime.now(timezone.utc) - timedelta(hours=24)


def main():
    bucket_name = config.pub_s3_bucket
    sources_files = list(config.sources_dir.glob("*"))

    file_modification_dates = {}

    for file_key in sources_files:
        if len(file_key.suffixes) <= 1:
            feed_file = "feed.json"
        else:
            feed_file = f"feed{file_key.suffixes[0]}.json"
        last_modified = get_last_modified_date(bucket_name, f"brave-today/{feed_file}")
        file_modification_dates[feed_file] = last_modified

    json_content = {}
    expired_files = []
    current_time = datetime.now(timezone.utc)
    total_files = len(sources_files)

    for file_key, last_modified in file_modification_dates.items():
        time_difference = current_time - last_modified
        is_file_expired = time_difference > timedelta(hours=3)
        json_content[str(file_key)] = {"expired": is_file_expired}
        if is_file_expired:
            expired_files.append(str(file_key))

    expired_count = len(expired_files)
    logger.info(f"Total regions {total_files}")
    logger.info(f"Total expired regions {expired_count}")

    expiry_threshold = math.floor(total_files * 0.8)
    if abs(total_files - expired_count) >= expiry_threshold:
        status = "success"
    else:
        status = "expired"

    logger.info(f"The status is {status}")
    result = {"status": status, "files": json_content}

    status_file = config.output_path / "latest-updated.json"
    with open(status_file, "w") as json_file:
        json.dump(result, json_file)

    logger.info(f"Uploading latest health check file to S3")
    upload_file(status_file, config.pub_s3_bucket, "latest-updated.json")

    if status == "expired":
        logger.info(f"Sending Alert to Sentry")
        capture_exception(
            ExpiredRegions(
                message=f"The following Regions are expired: {', '.join(expired_files)}"
            )
        )
        time.sleep(config.request_timeout)
        logger.info(f"Alert sent to Sentry")


if __name__ == "__main__":
    main()
