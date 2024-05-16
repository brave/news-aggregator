# Copyright (c) 2023 The Brave Authors. All rights reserved.
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at https://mozilla.org/MPL/2.0/. */

import logging
import math
import warnings
from datetime import datetime
from typing import Dict, Optional
from urllib.parse import urlparse, urlunparse

import dateparser
import feedparser
import requests
import structlog
from better_profanity import profanity
from fake_useragent import UserAgent
from prometheus_client import CollectorRegistry, Gauge, multiprocess
from requests import HTTPError, RequestException

from config import get_config
from utils import push_metrics_to_pushgateway

ua = UserAgent(browsers=["edge", "chrome", "firefox", "safari", "opera"])
config = get_config()

logging.getLogger("urllib3").setLevel(logging.ERROR)  # too many un-actionable warnings
logging.getLogger("metadata_parser").setLevel(
    logging.CRITICAL
)  # hide NotParsableFetchError messages
# disable the MarkupResemblesLocatorWarning
warnings.filterwarnings(
    "ignore", category=UserWarning, message=".*MarkupResemblesLocatorWarning.*"
)

logger = structlog.getLogger(__name__)

# adding custom bad words for profanity check
custom_badwords = ["vibrators", "hedonistic"]
profanity.add_censor_words(custom_badwords)

registry = CollectorRegistry()
multiprocess.MultiProcessCollector(registry)

PUBLISHER_ARTICLE_ALERT_NAME = "publisher_articles_count"
PUBLISHER_ARTICLE_ALERT_NAME_METRIC = Gauge(
    PUBLISHER_ARTICLE_ALERT_NAME,
    PUBLISHER_ARTICLE_ALERT_NAME,
    registry=registry,
    labelnames=["url"],
)

PUBLISHER_URL_ERR_ALERT_NAME = "publisher_url_error_count"
PUBLISHER_URL_ERR_ALERT_NAME_METRIC = Gauge(
    PUBLISHER_URL_ERR_ALERT_NAME,
    PUBLISHER_URL_ERR_ALERT_NAME,
    registry=registry,
    labelnames=["url"],
)


def get_with_max_size(
    url: str, max_bytes: Optional[int] = config.max_content_size
) -> bytes:
    """
    Get the content of a URL, raising an exception if the content is too large.

    Args:
        url (str): The URL to get the content from.
        max_bytes (Optional[int], optional): The maximum size of the content in bytes. Default is 10MB.

    Returns:
        bytes: The content of the URL.

    Raises:
        HTTPError: If there is an HTTP error with the URL.
        ValueError: If the content size exceeds the maximum size.
    """
    headers = {"User-Agent": ua.random, **config.default_headers}

    try:
        with requests.get(
            url, timeout=config.request_timeout, headers=headers
        ) as response:
            response.raise_for_status()

            if response.status_code != 200:
                raise HTTPError(f"HTTP error with status code {response.status_code}")

            content_length = response.headers.get("Content-Length")
            if (
                max_bytes is not None
                and content_length
                and int(content_length) > max_bytes
            ):
                raise ValueError("Content-Length too large")

            return response.content

    except RequestException as e:
        raise HTTPError(f"Failed to make request: {e}")


def download_feed(feed: str, max_feed_size: int = 10000000) -> Optional[Dict[str, str]]:
    """
    Downloads a feed from the given URL.

    Args:
        feed: The URL of the feed to download.
        max_feed_size: The maximum size of the feed to download. Defaults to 10000000.

    Returns:
        A dictionary containing the downloaded feed data and the key of the feed.
        Returns None if there is an error while downloading the feed.

    Raises:
        ReadTimeout: If the download times out.
        HTTPError: If there is an HTTP error while downloading the feed.
    """
    try:
        data = get_with_max_size(feed, max_feed_size)
        logger.debug(f"Downloaded feed: {feed}")
    except Exception:
        # Failed to get feed. I will try plain HTTP.
        try:
            u = urlparse(feed)
            u = u._replace(scheme="http")
            feed_url = urlunparse(u)
            data = get_with_max_size(feed_url, max_feed_size)
        except Exception as e:
            logger.error(f"Failed to get [{e}]: {feed}")
            prom_label = urlparse(feed).hostname
            prom_label = prom_label.replace(".", "_")
            push_metrics_to_pushgateway(
                PUBLISHER_URL_ERR_ALERT_NAME_METRIC, 1, prom_label, registry
            )
            return None

    return {"feed_cache": data, "key": feed}


def parse_rss(downloaded_feed):
    """
    Parses the downloaded RSS feed.

    Parameters:
        downloaded_feed (dict): A dictionary containing the downloaded feed, with the keys "key" and "feed_cache".

    Returns:
        None: If the feed fails to parse.

    Raises:
        Exception: If no articles are read from the feed.

    """
    report = {"size_after_get": None, "size_after_insert": 0}
    url, data = downloaded_feed["key"], downloaded_feed["feed_cache"]

    try:
        feed_cache = feedparser.parse(data)
        report["size_after_get"] = len(feed_cache["items"])
        if report["size_after_get"] == 0:
            logger.info(f"Read 0 articles from {url}")
            raise Exception(f"Read 0 articles from {url}")
    except Exception as e:
        logger.error(f"Feed failed to parse [{e}]: {url}")
        prom_label = urlparse(url).hostname
        prom_label = prom_label.replace(".", "_")
        push_metrics_to_pushgateway(
            PUBLISHER_ARTICLE_ALERT_NAME_METRIC, 1, prom_label, registry
        )
        return None

    feed_cache = dict(feed_cache)  # bypass serialization issues

    # TODO: insert feed updated into database in feed_lastbuild table

    if "bozo_exception" in feed_cache:
        del feed_cache["bozo_exception"]

    if "bozo" in feed_cache:
        del feed_cache["bozo"]

    return {"report": report, "feed_cache": feed_cache, "key": url}


def score_entries(entries):
    """
    Generates a list of scored entries based on the provided entries.

    Parameters:
        entries (list): A list of dictionaries representing the entries to be scored.

    Returns:
        list: A list of dictionaries representing the scored entries. Each dictionary contains the original entry
        along with an additional "score" field representing the calculated score.
    """
    out_entries = []
    variety_by_source = {}
    for entry in entries:
        seconds_ago = (
            datetime.utcnow() - dateparser.parse(entry["publish_time"])
        ).total_seconds()
        recency = math.log(seconds_ago) if seconds_ago > 0 else 0.1
        if entry["publisher_id"] in variety_by_source:
            last_variety = variety_by_source[entry["publisher_id"]]
        else:
            last_variety = 1.0
        variety = last_variety * 2.0
        score = recency * variety
        entry["score"] = score
        out_entries.append(entry)
        variety_by_source[entry["publisher_id"]] = variety
    return out_entries
