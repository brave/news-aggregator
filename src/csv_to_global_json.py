# Copyright (c) 2023 The Brave Authors. All rights reserved.
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at https://mozilla.org/MPL/2.0/. */

import csv
import re

import structlog
from fastapi.encoders import jsonable_encoder
from orjson import orjson
from pydantic import ValidationError

from config import get_config
from models.publisher import LocaleModel, PublisherGlobal
from utils import get_cover_infos_lookup, get_favicons_lookup, upload_file

config = get_config()
logger = structlog.getLogger(__name__)

locales_finder = re.compile(r"sources\.(.*)\.csv")

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
    "destination_domains": True,
    "locales": True,
    "publisher_id": True,
}


def main():
    """
    Main function that processes the source files and generates the publishers data.

    This function iterates over the source files in the configured sources directory. For each file,
    it extracts the locale from the file name using a regular expression. Then, it reads the file using
    `csv.DictReader` and processes each row to create a `PublisherGlobal` object.
    If the publisher ID is not already in the `publishers` dictionary, it sets additional properties
    like `favicon_url`, `cover_url`, and `background_color` using lookup dictionaries.
    It also creates a `LocaleModel` object and appends it to the `locales` list of the publisher.
    If the publisher ID already exists in the `publishers` dictionary, it retrieves the existing publisher
    object and appends a new `LocaleModel` object to its `locales` list.

    After processing all the source files, the function converts the `publishers` dictionary into a list of
    dictionaries using a list comprehension. The resulting list is then sorted by the `publisher_name` key.

    Finally, the function writes the publishers data as a JSON string to the output file using the `orjson.dumps`
     function. If the `no_upload` flag is not set, it also uploads the output file to a specified S3 bucket.

    Note:
    - The `publishers` dictionary stores publisher objects with the publisher ID as the key.
    - The `PublisherGlobal` object is created using the `**data` syntax, which unpacks the values from the
     row dictionary as keyword arguments.
    - The `LocaleModel` object is also created using the `**data` syntax, and the `locale` property is set to
    the extracted locale from the file name.
    - The `publisher_include_keys` variable is used to specify the keys to include in the dictionaries when converting
     the `publishers` dictionary to a list.

    Returns:
        None
    """
    publishers = {}
    source_files = config.sources_dir.glob("sources.*_*.csv")
    for source_file in source_files:
        locale = locales_finder.findall(source_file.name)[0]
        with open(source_file) as publisher_file_pointer:
            publisher_reader = csv.DictReader(publisher_file_pointer)
            for data in publisher_reader:
                try:
                    publisher: PublisherGlobal = PublisherGlobal(**data)

                    if publisher.publisher_id not in publishers:
                        publisher.favicon_url = favicons_lookup.get(
                            publisher.site_url, None
                        )
                        cover_info = cover_infos_lookup.get(
                            publisher.site_url,
                            {"cover_url": None, "background_color": None},
                        )
                        publisher.cover_url = cover_info.get("cover_url")
                        publisher.background_color = cover_info.get("background_color")

                        locale_builder = LocaleModel(**data)
                        locale_builder.locale = locale
                        publisher.locales.append(locale_builder)

                        publishers[publisher.publisher_id] = publisher

                    else:
                        existing_publisher = publishers[publisher.publisher_id]
                        locale_builder = LocaleModel(**data)
                        locale_builder.locale = locale
                        existing_publisher.locales.append(locale_builder)

                except ValidationError as e:
                    logger.info(f"{e} on {data}")

    publishers_data_as_list = [
        x.dict(include=publisher_include_keys) for x in publishers.values()
    ]

    publishers_data_as_list = sorted(
        publishers_data_as_list, key=lambda x: x["publisher_name"]
    )

    with open(f"{config.output_path / config.global_sources_file}", "wb") as f:
        f.write(orjson.dumps(jsonable_encoder(publishers_data_as_list)))

    logger.info(f"Generated {config.global_sources_file}")
    if not config.no_upload:
        upload_file(
            config.output_path / config.global_sources_file,
            config.pub_s3_bucket,
            f"{config.global_sources_file}",
        )


if __name__ == "__main__":
    main()
