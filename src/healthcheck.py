import json
from datetime import datetime, timedelta, timezone

import pytz
import structlog
from sentry_sdk import capture_exception

from config import get_config
from utils import ExpiredRegions, s3_client, upload_file

logger = structlog.getLogger(__name__)
config = get_config()


def main():
    bucket_name = config.pub_s3_bucket
    sources_files = list(config.sources_dir.glob("*"))

    # Initialize an empty dict to store the results
    file_modification_dates = {}

    # Iterate through the list of file keys and retrieve the last modified date
    for file_key in sources_files:
        if len(file_key.suffixes) <= 1:
            feed_file = "brave-today/feed" + ".json"
        else:
            feed_file = "brave-today/feed" + file_key.suffixes[0] + ".json"
        try:
            response = s3_client.head_object(Bucket=bucket_name, Key=feed_file)
            last_modified = response["LastModified"]
            file_modification_dates[feed_file] = last_modified.astimezone(pytz.utc)
        except Exception as e:
            file_modification_dates[feed_file] = datetime.now(timezone.utc) - timedelta(
                hours=24
            )
            logger.error(f"Error retrieving last modified date for {feed_file}: {e}")

    json_content = {}
    expired_files = []
    expired_count = 0
    current_time = datetime.now(timezone.utc)
    total_files = len(list(sources_files))

    # Check if any files are older than 3 hours
    for file_key, last_modified in file_modification_dates.items():
        time_difference = current_time - last_modified
        is_file_expired = time_difference > timedelta(hours=3)
        json_content[file_key.__str__()] = {"expired": is_file_expired}
        if is_file_expired:
            expired_count += 1
            expired_files.append(file_key.__str__())

    # Determine the status based on the expiration
    # Check if less than 80% of the files are expired
    expiry_threshold = 0.8  # 80%
    expired = (expired_count / total_files) < expiry_threshold
    status = "expired" if expired < 0.8 else "success"

    # Create a dict to represent the result including status
    result = {"status": status, "files": json_content}

    status_file = config.output_path / "latest-updated.json"
    # Write the result as JSON to file
    with open(status_file.__str__(), "w") as json_file:
        json_file.write(json.dumps(result))

    # Upload the local JSON file to S3
    upload_file(status_file, config.pub_s3_bucket, "latest-updated.json")

    # Send a message to Sentry about the expired files
    if expired_files:
        capture_exception(
            ExpiredRegions(
                message=f"The following Regions are expired: {', '.join(expired_files)}"
            ),
            level="critical",
        )


if __name__ == "__main__":
    main()
