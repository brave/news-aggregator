# Copyright (c) 2023 The Brave Authors. All rights reserved.
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at https://mozilla.org/MPL/2.0/. */

from multiprocessing.pool import Pool, ThreadPool
from typing import List, Tuple
from urllib.parse import urljoin

import metadata_parser
import requests
import structlog
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from orjson import orjson
from requests import HTTPError

import image_processor_sandboxed
from config import get_config
from utils import get_all_domains, upload_file, uri_validator

ua = UserAgent(browsers=["edge", "chrome", "firefox", "safari", "opera"])

config = get_config()
logger = structlog.getLogger(__name__)
im_proc = image_processor_sandboxed.ImageProcessor(
    config.private_s3_bucket, s3_path="brave-today/favicons/{}", force_upload=True
)

# In seconds. Tested with 5s, but it's too low for a bunch of sites (I'm looking
# at you https://skysports.com).
REQUEST_TIMEOUT = 15


def get_favicon(domain: str) -> Tuple[str, str]:  # noqa: C901
    # Set the default favicon path. If we don't find something better, we'll use
    # this.
    default_icon_url = "/favicon.ico"
    icon_url = None
    try:
        icon_url = (
            f"https://t0.gstatic.com/faviconV2?client=SOCIAL&"
            f"type=FAVICON&fallback_opts=TYPE,SIZE,URL&url={domain}&size=64"
        )
        res = requests.get(
            icon_url,
            timeout=REQUEST_TIMEOUT,
            headers={"User-Agent": ua.random, **config.default_headers},
        )

        res.raise_for_status()

        if res.status_code != 200:  # raise for status is not working with 3xx error
            raise HTTPError(f"Http error with status code {res.status_code}")

    except Exception as e:
        logger.info(
            f"Failed to download HTML for {domain} with exception {e}. Using default icon path {icon_url}"
        )

    if icon_url is None:
        try:
            page = metadata_parser.MetadataParser(
                url=domain,
                support_malformed=True,
                url_headers={"User-Agent": ua.random, **config.default_headers},
                search_head_only=True,
                strategy=["page", "meta", "og", "dc"],
                requests_timeout=config.request_timeout,
            )
            icon_url = page.get_metadata_link("image")
        except metadata_parser.NotParsableFetchError as e:
            if e.code and e.code not in (403, 429, 500, 502, 503):
                logger.error(f"Error parsing [{domain}]: {e}")
        except (UnicodeDecodeError, metadata_parser.NotParsable) as e:
            logger.error(f"Error parsing: {domain} -- {e}")
        except Exception as e:
            logger.error(f"Error parsing: {domain} -- {e}")

    if icon_url is None:
        try:
            response = requests.get(
                domain,
                timeout=REQUEST_TIMEOUT,
                headers={"User-Agent": ua.random, **config.default_headers},
            )
            soup = BeautifulSoup(response.text, features="lxml")
            icon = soup.find("link", rel="icon")

            # Some sites may use an icon with a different rel.
            if not icon:
                icon = soup.find("link", rel="shortcut icon")
            if not icon:
                icon = soup.find("link", rel="apple-touch-icon")

            # Check if the icon exists, and the href is not empty. Surprisingly,
            # some sites actually do this (https://coinchoice.net/ + more).
            if icon and icon.get("href"):
                icon_url = icon.get("href")
        except Exception as e:
            logger.info(
                f"Failed to download HTML for {domain} with exception {e}. Using default icon path {icon_url}"
            )

        if icon_url is None:
            # We need to resolve relative urls, so we send something sensible to the client.
            icon_url = urljoin(domain, icon_url)
        else:
            icon_url = urljoin(domain, default_icon_url)

        if not uri_validator(icon_url):
            icon_url = None

    return domain, icon_url


def process_favicons_image(item):
    domain = ""
    padded_icon_url = None
    try:
        domain, icon_url = item
        try:
            cache_fn = im_proc.cache_image(icon_url)
        except Exception as e:
            cache_fn = None
            logger.error(f"im_proc.cache_image failed [{e}]: {icon_url}")
        if cache_fn:
            padded_icon_url = f"{config.pcdn_url_base}/brave-today/favicons/{cache_fn}"
        else:
            padded_icon_url = None

    except ValueError as e:
        logger.info(f"Tuple unpacking error {e}")

    logger.info(f"The padded image of the {domain} is {padded_icon_url}")

    return domain, padded_icon_url


if __name__ == "__main__":
    domains = list(set(get_all_domains()))
    logger.info(f"Processing {len(domains)} domains")

    favicons: List[Tuple[str, str]]
    with ThreadPool(config.thread_pool_size) as pool:
        favicons = pool.map(get_favicon, domains)

    processed_favicons: List[Tuple[str, str]]
    with Pool(config.concurrency) as pool:
        processed_favicons = pool.map(process_favicons_image, favicons)

    with open(config.output_path / config.favicon_lookup_file, "wb") as f:
        f.write(orjson.dumps(dict(processed_favicons)))

    logger.info("Fetched all the favicons!")

    if not config.no_upload:
        upload_file(
            config.output_path / config.favicon_lookup_file,
            config.pub_s3_bucket,
            f"{config.favicon_lookup_file}",
        )
        logger.info(f"{config.favicon_lookup_file} is upload to S3")
