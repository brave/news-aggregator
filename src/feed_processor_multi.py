# Copyright (c) 2023 The Brave Authors. All rights reserved.
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at https://mozilla.org/MPL/2.0/. */

import hashlib
import html
import json
import logging
import math
import shutil
import sys
import time
import warnings
from collections import defaultdict
from datetime import datetime, timedelta
from functools import partial
from multiprocessing import Pool as ProcessPool
from multiprocessing.pool import ThreadPool
from pathlib import Path
from urllib.parse import quote, urlparse, urlunparse

import bleach
import dateparser
import feedparser
import metadata_parser
import orjson
import pytz
import requests
import structlog
import unshortenit
from better_profanity import profanity
from bs4 import BeautifulSoup as BS
from fake_useragent import UserAgent
from prometheus_client import CollectorRegistry, Gauge, multiprocess
from requests.exceptions import (
    ConnectTimeout,
    HTTPError,
    InvalidURL,
    ReadTimeout,
    SSLError,
    TooManyRedirects,
)

from config import get_config
from src import image_processor_sandboxed
from utils import push_metrics_to_pushgateway, upload_file

ua = UserAgent(browsers=["edge", "chrome", "firefox", "safari", "opera"])

config = get_config()

im_proc = image_processor_sandboxed.ImageProcessor(config.private_s3_bucket)

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


def get_with_max_size(url, max_bytes=10000000):
    response = requests.get(
        url,
        timeout=config.request_timeout,
        headers={"User-Agent": ua.random},
    )
    response.raise_for_status()

    if response.status_code != 200:  # raise for status is not working with 3xx error
        raise HTTPError(f"Http error with status code {response.status_code}")

    if (
        response.headers.get("Content-Length")
        and int(response.headers.get("Content-Length")) > max_bytes
    ):
        raise ValueError("Content-Length too large")

    return response.content


def download_feed(feed, max_feed_size=10000000):
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
        except ReadTimeout as e:
            logger.error(f"Failed to get feed: {feed} ({e})")
            prom_label = urlparse(feed).hostname
            prom_label = prom_label.replace(".", "_")
            push_metrics_to_pushgateway(
                PUBLISHER_URL_ERR_ALERT_NAME_METRIC, 1, prom_label, registry
            )
            return None
        except HTTPError as e:
            prom_label = urlparse(feed).hostname
            prom_label = prom_label.replace(".", "_")
            logger.error(f"Failed to get feed: {feed} ({e})")
            push_metrics_to_pushgateway(
                PUBLISHER_URL_ERR_ALERT_NAME_METRIC, 1, prom_label, registry
            )
            return None
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

    if "bozo_exception" in feed_cache:
        del feed_cache["bozo_exception"]

    return {"report": report, "feed_cache": feed_cache, "key": url}


def process_image(item):
    if item["img"] is None or item["img"] == "":
        item["img"] = ""
        item["padded_img"] = ""
        return item

    else:
        try:
            cache_fn = im_proc.cache_image(item["img"])
        except Exception as e:
            cache_fn = None
            logger.error(f"im_proc.cache_image failed [{e}]: {item['img']}")
        if cache_fn:
            parsed_url = urlparse(cache_fn)
            if parsed_url.scheme:
                item["padded_img"] = cache_fn
            else:
                item[
                    "padded_img"
                ] = f"{config.pcdn_url_base}/brave-today/cache/{cache_fn}"
        else:
            item["img"] = ""
            item["padded_img"] = ""

    return item


def get_article_img(article):  # noqa: C901
    # image determination
    img_url = ""
    if article.get("image"):
        img_url = article["image"]

    elif article.get("urlToImage"):
        img_url = article["urlToImage"]

    elif article.get("media_content"):
        largest_width = 0
        for content in article.get("media_content"):
            if int(content.get("width") or 0) > largest_width:
                largest_width = int(content.get("width"))
                img_url = content.get("url")

    elif article.get("media_thumbnail"):
        largest_width = 0
        for content in article.get("media_thumbnail"):
            if int(content.get("width") or 0) > largest_width:
                largest_width = int(content.get("width"))
                img_url = content.get("url")

    elif article.get("summary"):
        soup = BS(article["summary"], features="html.parser")
        image_tags = soup.find_all("img")
        for img_tag in image_tags:
            if "src" in img_tag.attrs:
                img_url = img_tag.get("src")
                break

    elif article.get("content"):
        soup = BS(article["content"][0]["value"], features="html.parser")
        image_tags = soup.find_all("img")
        for img_tag in image_tags:
            if "src" in img_tag.attrs:
                img_url = img_tag.get("src")
                break

    return img_url


def process_articles(article, _publisher):  # noqa: C901
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

    out_article["img"] = get_article_img(article)

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
    out_article["creative_instance_id"] = _publisher["creative_instance_id"]

    return out_article


def unshorten_url(out_article):
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

    return out_article


def get_popularity_score(out_article):
    url = config.bs_pop_endpoint + out_article["url"]
    try:
        response = get_with_max_size(url)
        pop_response = orjson.loads(response)
        pop_score = pop_response.get("popularity").get("popularity")
        pop_score_agg = sum(pop_score.values())
        out_article["pop_score"] = pop_score_agg
    except Exception as e:
        logger.error(f"Unable to get the pop score for {url} due to {e}")
        out_article["pop_score"] = None

    return out_article


def get_predicted_category(out_article):
    try:
        pred_results = dict()
        nu_api_response = requests.post(
            url=config.nu_api_url,
            json=[out_article],
            headers=config.nu_api_headers,
            timeout=config.request_timeout,
        )
        api_response = nu_api_response.json()
        pred_category_results = api_response.get("results")[0]
        pred_results["reliability"] = pred_category_results["reliability"]

        for pred in pred_category_results.get("categories"):
            pred_results["category"] = pred["name"]
            pred_results["confidence"] = pred["confidence"]
            break

        out_article["predicted_category"] = pred_results
    except Exception as e:
        logger.error(f"Unable to get the pop score for predicted category due to {e}")
        out_article["predicted_category"] = None

    return out_article


def check_images_in_item(article, _publishers):  # noqa: C901
    if article["img"]:
        try:
            parsed_img_url = urlparse(article["img"])
            if not parsed_img_url.scheme:
                parsed = parsed_img_url._replace(scheme="https")
                url = urlunparse(parsed)
                article["img"] = url

            if len(parsed_img_url.path) < 4:
                article["img"] = ""

        except Exception as e:
            logger.error(f"Can't parse image [{article['img']}]: {e}")
            article["img"] = ""

    if (
        article["img"] == ""
        or _publishers[article["publisher_id"]]["og_images"] is True
    ):
        # if we came out of this without an image, lets try to get it from opengraph
        try:
            page = metadata_parser.MetadataParser(
                url=article["url"],
                support_malformed=True,
                url_headers={"User-Agent": ua.random},
                search_head_only=True,
                strategy=["page", "meta", "og", "dc"],
                requests_timeout=config.request_timeout,
            )
            article["img"] = page.get_metadata_link("image")
        except metadata_parser.NotParsableFetchError as e:
            if e.code and e.code not in (403, 429, 500, 502, 503):
                logger.error(f"Error parsing [{article['url']}]: {e}")
        except (UnicodeDecodeError, metadata_parser.NotParsable) as e:
            logger.error(f"Error parsing: {article['url']} -- {e}")
        except Exception as e:
            logger.error(f"Error parsing: {article['url']} -- {e}")

    article["padded_img"] = article["img"]

    return article


def scrub_html(feed: dict):
    """Scrubbing HTML of all entries that will be written to feed"""
    for key in feed.keys():
        try:
            feed[key] = bleach.clean(feed[key], strip=True)
            feed[key] = feed[key].replace(
                "&amp;", "&"
            )  # workaround limitation in bleach
        except Exception:
            feed[key] = feed[key]

    return feed


def score_entries(entries):
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


class FeedProcessor:
    def __init__(self, _publishers: dict, _output_path: Path):
        self.report = defaultdict(dict)  # holds reports and stats of all actions
        self.feeds = defaultdict(dict)
        self.publishers: dict = _publishers
        self.output_path: Path = _output_path

    def check_images(self, items):
        out_items = []
        logger.info(f"Checking images for {len(items)} items...")
        with ThreadPool(config.thread_pool_size) as pool:
            for item in pool.imap_unordered(
                partial(check_images_in_item, _publishers=self.feeds), items
            ):
                out_items.append(item)

        logger.info(f"Caching images for {len(out_items)} items...")
        with ProcessPool(config.concurrency) as pool:
            result = []
            for item in pool.imap_unordered(process_image, out_items):
                result.append(item)
        return result

    def download_feeds(self):
        downloaded_feeds = []
        feed_cache = {}
        logger.info(f"Downloading {len(self.publishers)} feeds...")
        with ThreadPool(config.thread_pool_size) as pool:
            for result in pool.imap_unordered(
                download_feed,
                [self.publishers[key]["feed_url"] for key in self.publishers],
            ):
                if not result:
                    continue
                downloaded_feeds.append(result)

        with ProcessPool(config.concurrency) as pool:
            for result in pool.imap_unordered(parse_rss, downloaded_feeds):
                if not result:
                    continue

                self.report["feed_stats"][result["key"]] = result["report"]
                feed_cache[result["key"]] = result["feed_cache"]
                self.feeds[
                    self.publishers[result["key"]]["publisher_id"]
                ] = self.publishers[result["key"]]

        return feed_cache

    def get_rss(self):
        raw_entries = []
        entries = []
        self.report["feed_stats"] = {}

        feed_cache = self.download_feeds()

        logger.info(
            f"Fixing up and extracting the data for the items in {len(feed_cache)} feeds..."
        )
        for key in feed_cache:
            logger.debug(f"processing: {key}")
            start_time = time.time()
            with ProcessPool(config.concurrency) as pool:
                for out_item in pool.imap_unordered(
                    partial(process_articles, _publisher=self.publishers[key]),
                    feed_cache[key]["entries"][: self.publishers[key]["max_entries"]],
                ):
                    if out_item:
                        raw_entries.append(out_item)
                    self.report["feed_stats"][key]["size_after_insert"] += 1
            end_time = time.time()
            logger.debug(
                f"processed {key} in {round((end_time - start_time) * 1000)} ms"
            )

        logger.info(f"Un-shorten the URL of {len(raw_entries)}")
        with ThreadPool(config.thread_pool_size) as pool:
            for result in pool.imap_unordered(unshorten_url, raw_entries):
                if not result:
                    continue
                entries.append(result)

        raw_entries.clear()

        logger.info(f"Getting the Popularity score the URL of {len(entries)}")
        with ThreadPool(config.thread_pool_size) as pool:
            for result in pool.imap_unordered(get_popularity_score, entries):
                if not result:
                    continue
                raw_entries.append(result)

        entries.clear()

        logger.info(f"Getting the Pred categorize the API of {len(raw_entries)}")
        with ThreadPool(config.thread_pool_size) as pool:
            for result in pool.imap_unordered(get_predicted_category, raw_entries):
                if not result:
                    continue
                entries.append(result)

        return entries

    def aggregate_rss(self):
        entries = []
        filtered_entries = []
        entries += self.get_rss()

        logger.info(f"Getting images for {len(entries)} items...")
        fixed_entries = self.check_images(entries)
        entries.clear()

        logger.info(f"Scrubbing {len(fixed_entries)} items...")
        with ProcessPool(config.concurrency) as pool:
            for result in pool.imap_unordered(scrub_html, fixed_entries):
                filtered_entries.append(result)
        fixed_entries.clear()

        sorted_entries = list({d["url_hash"]: d for d in filtered_entries}.values())

        logger.info(f"Sorting for {len(sorted_entries)} items...")
        sorted_entries = sorted(sorted_entries, key=lambda entry: entry["publish_time"])
        sorted_entries.reverse()
        filtered_entries.clear()

        filtered_entries = score_entries(sorted_entries)
        return filtered_entries

    def aggregate(self):
        with open(self.output_path, "wb") as _f:
            feeds = self.aggregate_rss()
            _f.write(orjson.dumps(feeds))

    async def aggregate_shards(self):
        by_category = {}
        feeds = self.aggregate_rss()
        for item in feeds:
            if not item["category"] in by_category:
                by_category[item["category"]] = [item]
            else:
                by_category[item["category"]].append(item)
        for key in by_category:
            with open(f"feed/category/{key}.json", "w") as _f:
                _f.write(json.dumps(by_category[key]))


if __name__ == "__main__":
    if len(sys.argv) > 1:
        category = sys.argv[1]
    else:
        category = "feed"

    with open(config.output_path / f"{category}.json") as f:
        publishers = orjson.loads(f.read())
        output_path = config.output_feed_path / f"{category}.json-tmp"
        fp = FeedProcessor(publishers, output_path)
        fp.aggregate()
        shutil.copyfile(
            config.output_feed_path / f"{category}.json-tmp",
            config.output_feed_path / f"{category}.json",
        )

        if not config.no_upload:
            upload_file(
                config.output_feed_path / f"{category}.json",
                config.pub_s3_bucket,
                f"brave-today/{category}{str(config.sources_file).replace('sources', '')}.json",
            )
            # Temporarily upload also with incorrect filename as a stopgap for
            # https://github.com/brave/brave-browser/issues/20114
            # Can be removed once fixed in the brave-core client for all Desktop users.
            upload_file(
                config.output_feed_path / f"{category}.json",
                config.pub_s3_bucket,
                f"brave-today/{category}{str(config.sources_file).replace('sources', '')}json",
            )
    with open(config.output_path / "report.json", "w") as f:
        f.write(json.dumps(fp.report))
