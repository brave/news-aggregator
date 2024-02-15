# Copyright (c) 2023 The Brave Authors. All rights reserved.
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at https://mozilla.org/MPL/2.0/. */

import csv

import orjson
import structlog

from config import get_config
from models.publisher import PublisherModel
from utils import get_cover_infos_lookup, get_favicons_lookup, upload_file

config = get_config()

logger = structlog.getLogger(__name__)

favicons_lookup = get_favicons_lookup()
cover_infos_lookup = get_cover_infos_lookup()

publisher_include_keys = {
    "enabled": True,
    "publisher_name": True,
    "category": True,
    "site_url": True,
    "feed_url": True,
    "favicon_url": True,
    "cover_url": True,
    "background_color": True,
    "score": True,
    "channels": True,
    "rank": True,
    "publisher_id": True,
    "destination_domains": True,
}

feed_include_keys = {
    "category": True,
    "publisher_name": True,
    "content_type": True,
    "publisher_domain": True,
    "publisher_id": True,
    "max_entries": True,
    "og_images": True,
    "creative_instance_id": True,
    "channels": True,
    "feed_url": True,
    "site_url": True,
    "destination_domains": True,
}


def main():
    """
    This function is the main entry point of the program. It performs the following tasks:
    - Constructs the file paths for the publisher file, feed output, and sources output.
    - Reads the publisher file and creates a list of PublisherModel objects.
    - Sorts the list of PublisherModel objects based on the publisher name.
    - Writes the list of publishers data by URL to the feed output file.
    - Writes the list of publishers data as a list to the sources output file.
    - Uploads the sources output file to the specified S3 bucket.

    Parameters:
    None

    Returns:
    None
    """
    publisher_file_path = f"{config.sources_dir / config.sources_file}.csv"
    feed_sources = "feed_source.json"
    publisher_sources = "sources.json"

    feed_sources_output_path = config.output_path / feed_sources
    sources_output_path = config.output_path / publisher_sources

    try:
        with open(publisher_file_path) as publisher_file_pointer:
            publisher_reader = csv.DictReader(publisher_file_pointer)
            publishers = [
                PublisherModel(
                    **data,
                    favicon_url=favicons_lookup.get(data["Domain"], None),
                    cover_url=cover_infos_lookup.get(
                        data["Domain"], {"cover_url": None, "background_color": None}
                    )["cover_url"],
                    background_color=cover_infos_lookup.get(
                        data["Domain"], {"cover_url": None, "background_color": None}
                    )["background_color"],
                )
                for data in publisher_reader
            ]
    except FileNotFoundError as e:
        raise e
    except csv.Error as e:
        raise e
    except Exception as e:
        raise e

    publishers_data_by_url = {
        str(x.feed_url): x.dict(include=feed_include_keys) for x in publishers
    }

    publishers_data_as_list = [
        x.dict(include=publisher_include_keys) for x in publishers
    ]

    publishers_data_as_list = sorted(
        publishers_data_as_list, key=lambda x: x["publisher_name"]
    )

    with open(feed_sources_output_path, "wb") as f:
        f.write(orjson.dumps(publishers_data_by_url))

    with open(sources_output_path, "wb") as f:
        f.write(orjson.dumps(publishers_data_as_list))

    if not config.no_upload:
        upload_file(
            sources_output_path, config.pub_s3_bucket, f"{config.sources_file}.json"
        )
        # Temporarily upload also with incorrect filename as a stopgap for
        # https://github.com/brave/brave-browser/issues/20114
        # Can be removed once fixed in the brave-core client for all Desktop users.
        upload_file(
            sources_output_path, config.pub_s3_bucket, f"{config.sources_file}json"
        )


if __name__ == "__main__":
    main()
