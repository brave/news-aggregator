import time
from collections import defaultdict
from functools import partial
from multiprocessing import Pool as ProcessPool
from multiprocessing.pool import ThreadPool
from pathlib import Path

import orjson
import structlog

from aggregator.external_services import get_popularity_score, get_predicted_channels
from aggregator.image_fetcher import (
    check_images_in_item,
    check_small_image,
    process_image,
)
from aggregator.image_processor_sandboxed import get_image_with_max_size
from aggregator.parser import download_feed, parse_rss, score_entries
from aggregator.processor import process_articles, scrub_html, unshorten_url
from config import get_config

config = get_config()
logger = structlog.get_logger()


class Aggregator:
    def __init__(self, _publishers: dict, _output_path: Path):
        self.report = defaultdict(dict)  # holds reports and stats of all actions
        self.feeds = defaultdict(dict)
        self.publishers: dict = _publishers
        self.output_path: Path = _output_path

    def check_images(self, items):
        """
        Checks the images for the given items.

        Args:
            items (list): A list of items to check the images for.

        Returns:
            list: A list of items with the checked images.
        """
        result = []
        out_items = []
        logger.info(f"Checking images for padding from {len(items)} items...")
        with ThreadPool(config.thread_pool_size) as pool:
            for item, content, is_large in pool.imap_unordered(
                get_image_with_max_size, items
            ):
                result.append((item, content, is_large))

        logger.info(f"Checking images for {len(items)} items...")
        with ProcessPool(config.concurrency) as pool:
            for item in pool.imap_unordered(check_small_image, result):
                out_items.append(item)

        result.clear()

        with ThreadPool(config.thread_pool_size) as pool:
            for item in pool.imap_unordered(
                partial(check_images_in_item, _publishers=self.feeds), out_items
            ):
                result.append(item)

        out_items.clear()

        padded_result = [(item[0], item[1]) for item in result if item[2] is True]
        out_items = [item[0] for item in result if item[2] is False]
        logger.info(f"Caching images for items...")
        with ProcessPool(config.concurrency) as pool:
            for item in pool.imap_unordered(process_image, padded_result):
                out_items.append(item)

        return out_items

    def download_feeds(self):
        """
        Downloads feeds from the publishers and parses them.

        Returns:
            feed_cache (dict): A dictionary containing the parsed feeds, with the publisher's key as the key and
            the parsed feed as the value.
        """
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

    def normalize_pop_score(self, articles):
        max_pop_score = max(articles, key=lambda x: x["pop_score"])["pop_score"]
        min_pop_score = min(articles, key=lambda x: x["pop_score"])["pop_score"]
        for article in articles:
            article_pop_score = article["pop_score"]
            normalized_pop_score = (
                config.pop_score_range
                * (
                    (article_pop_score - min_pop_score)
                    / (max_pop_score - min_pop_score)
                )
                if max_pop_score != min_pop_score
                else 1,
            )
            article["pop_score"] = max(normalized_pop_score[0], 1.0)

    def get_rss(self):  # noqa: C901
        """
        Retrieves the RSS feed data.

        Returns:
            - If `config.sources_file` is "sources.en_US", a list of entries with predicted categories.
            - Otherwise, a list of entries with popularity scores.
        """
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

        self.normalize_pop_score(raw_entries)

        if str(config.sources_file) == "sources.en_US":
            entries.clear()
            logger.info(f"Getting the Predicted Channel the API of {len(raw_entries)}")
            with ThreadPool(config.thread_pool_size) as pool:
                for result in pool.imap_unordered(get_predicted_channels, raw_entries):
                    if not result:
                        continue
                    entries.append(result)
            return entries

        return raw_entries

    def aggregate_rss(self):
        """
        Aggregates RSS entries by performing the following steps:

        1. Retrieves RSS entries using the `get_rss` method.
        2. Checks and fixes images for each entry using the `check_images` method.
        3. Scrubs HTML content in parallel using a `ProcessPool` and the `scrub_html` function.
        4. Removes duplicate entries based on the `url_hash` field.
        5. Sorts the entries based on the `publish_time` field in descending order.
        6. Calculates scores for each entry using the `score_entries` function.

        Returns a list of filtered entries.
        """
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
        """
        Aggregates the RSS feeds and writes the result to the output file.

        Parameters:
            None

        Returns:
            None
        """
        with open(self.output_path, "wb") as _f:
            feeds = self.aggregate_rss()
            _f.write(orjson.dumps(feeds))
