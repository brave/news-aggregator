# Copyright (c) 2023 The Brave Authors. All rights reserved.
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at https://mozilla.org/MPL/2.0/. */

import hashlib
import html
from datetime import datetime, timedelta
from urllib.parse import quote, urljoin, urlparse, urlunparse

import bleach
import dateparser
import pytz
import requests
import structlog
import unshortenit
from better_profanity import profanity
from bs4 import BeautifulSoup as BS
from fake_useragent import UserAgent
from requests.exceptions import (
    ConnectTimeout,
    InvalidURL,
    ReadTimeout,
    SSLError,
    TooManyRedirects,
)

from aggregator.image_fetcher import get_article_img
from config import get_config
from db_crud import get_article

logger = structlog.getLogger(__name__)

config = get_config()
ua = UserAgent(browsers=["edge", "chrome", "firefox", "safari", "opera"])


def process_articles(article, _publisher):  # noqa: C901
    """
    Process the given article and return a dictionary containing the processed data.

    Args:
        article (dict): The article to be processed.
        _publisher (dict): The publisher information.

    Returns:
        dict: A dictionary containing the processed data of the article.
              Returns None if the article is not valid or should be skipped.
    """
    out_article = {}

    # Process Title of the article
    if not article.get("title"):
        # No title. Skip.
        return None

    out_article["title"] = BS(article["title"], features="html.parser").get_text()
    out_article["title"] = html.unescape(out_article["title"])

    # Filter the offensive articles
    if profanity.contains_profanity(out_article.get("title").lower()):
        return None

    # Process article URL
    if article.get("link"):
        out_article["link"] = article["link"]
    elif article.get("url"):
        out_article["link"] = article["url"]
    else:
        return None  # skip (can't find link)

    parsed_article_url = urlparse(out_article["link"])
    if len(parsed_article_url.path) < 4:
        return None  # skip (link is the same as the publisher's site URL)

    # Process published time
    if article.get("updated"):
        out_article["publish_time"] = dateparser.parse(article.get("updated"))
    elif article.get("published"):
        out_article["publish_time"] = dateparser.parse(article.get("published"))
    else:
        return None  # skip (no update field)

    if out_article.get("publish_time") is None:
        return None

    if out_article["publish_time"].tzinfo is None:
        config.tz.localize(out_article["publish_time"])

    out_article["publish_time"] = out_article["publish_time"].astimezone(pytz.utc)

    now_utc = datetime.now().replace(tzinfo=pytz.utc)
    if _publisher["content_type"] != "product":
        if out_article["publish_time"] > now_utc or out_article["publish_time"] < (
            now_utc - timedelta(days=60)
        ):
            return None  # skip (newer than now() or older than 1 month)

    out_article["publish_time"] = out_article["publish_time"].strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    try:
        image_url = get_article_img(article)

        parsed_url = urlparse(image_url)
        if not parsed_url.netloc and image_url:
            # If not, update the URL by joining it with the publisher's URL
            image_url = urljoin(_publisher["site_url"], image_url)

        if len(parsed_url.path) < 4 and image_url:
            image_url = ""

        out_article["img"] = image_url
    except Exception as e:
        logger.error(f"Error retrieving image from URL {article.get('url')}: {e}")
        out_article["img"] = ""

    # Add some fields
    out_article["category"] = _publisher.get("category")
    if article.get("description"):
        out_article["description"] = BS(
            article["description"], features="html.parser"
        ).get_text()
    else:
        out_article["description"] = ""

    out_article["content_type"] = _publisher["content_type"]
    if out_article["content_type"] == "audio":
        out_article["enclosures"] = article["enclosures"]
    if out_article["content_type"] == "product":
        out_article["offers_category"] = article["category"]

    out_article["publisher_id"] = _publisher["publisher_id"]
    out_article["publisher_name"] = _publisher["publisher_name"]
    out_article["channels"] = list(_publisher["channels"])
    out_article["creative_instance_id"] = _publisher["creative_instance_id"]

    return out_article


def unshorten_url(out_article):
    """
    Unshortens a URL in the given output article.

    Args:
        out_article (dict): The output article containing the URL to unshorten.

    Returns:
        dict or None: The modified output article with the unshortened URL, or None if unshortening failed.
    """
    unshortener = unshortenit.UnshortenIt(
        default_timeout=config.request_timeout,
        default_headers={"User-Agent": ua.random},
    )

    try:
        out_article["url"] = unshortener.unshorten(out_article["link"])
        out_article.pop("link", None)
    except (
        requests.exceptions.ConnectionError,
        ConnectTimeout,
        InvalidURL,
        ReadTimeout,
        SSLError,
        TooManyRedirects,
    ):
        return None  # skip (unshortener failed)
    except Exception as e:
        logger.error(f"unshortener failed [{out_article.get('link')}]: {e}")
        return None  # skip (unshortener failed)

    url_hash = hashlib.sha256(out_article["url"].encode("utf-8")).hexdigest()
    parts = urlparse(out_article["url"])
    parts = parts._replace(path=quote(parts.path))
    encoded_url = urlunparse(parts)
    out_article["url"] = encoded_url
    out_article["url_hash"] = url_hash

    processed_article = get_article(
        url_hash, str(config.sources_file).replace("sources.", "")
    )

    if processed_article:
        return None, processed_article

    return out_article, None


def scrub_html(feed: dict):
    """
    Scrubs the HTML content in the given feed dictionary.

    Parameters:
        feed (dict): The dictionary containing the HTML content to be scrubbed.

    Returns:
        dict: The modified feed dictionary with the HTML content scrubbed.
    """
    for key in feed.keys():
        try:
            feed[key] = bleach.clean(feed[key], strip=True)
            feed[key] = feed[key].replace(
                "&amp;", "&"
            )  # workaround limitation in bleach
        except Exception:
            feed[key] = feed[key]

    return feed
