# Copyright (c) 2023 The Brave Authors. All rights reserved.
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at https://mozilla.org/MPL/2.0/. */

import json
import os

import feedparser

from aggregator.aggregate import Aggregator
from aggregator.parser import download_feed, score_entries
from aggregator.processor import scrub_html
from config import get_config

config = get_config()


def test_feed_processor_download():
    result = download_feed("https://brave.com/blog/index.xml")
    assert result


def test_feed_processor_aggregate():
    feeds = json.loads(open(config.tests_data_dir / "test.json").read())
    fp = Aggregator(feeds, config.output_feed_path / "test.json")
    fp.aggregate()
    assert os.stat(config.output_feed_path / "test.json").st_size != 0

    with open(config.output_feed_path / "test.json") as f:
        data = json.loads(f.read())
    assert data
    assert len(data) != 0


def test_check_images():
    feeds = json.loads(open(config.tests_data_dir / "test.json").read())
    fp = Aggregator(feeds, config.output_feed_path / "test.json")
    data = [feedparser.parse(config.tests_data_dir / "test.rss")["items"][0]]
    data[0]["img"] = data[0]["media_content"][0]["url"]
    data[0]["publisher_id"] = ""
    fp.feeds[""] = {"og_images": False}
    assert fp.check_images(data)


def test_download_feeds():
    with open(config.tests_data_dir / "test.json") as f:
        data = json.loads(f.read())
    data = {
        "https://brave.com/blog/index.xml": data["https://brave.com/blog/index.xml"]
    }
    fp = Aggregator(data, config.output_feed_path / "test.json")
    fp.report["feed_stats"] = {}
    result = fp.download_feeds()
    assert len(result) != 0


def test_get_rss():
    with open(config.tests_data_dir / "test.json") as f:
        data = json.loads(f.read())
    data = {
        "https://brave.com/blog/index.xml": data["https://brave.com/blog/index.xml"]
    }
    fp = Aggregator(data, config.output_feed_path / "test.json")
    fp.report["feed_stats"] = {}
    result = fp.get_rss()
    assert len(result) != 0


def test_fixup_entries():
    with open(config.tests_data_dir / "test.json") as f:
        data = json.loads(f.read())
    data = {
        "https://brave.com/blog/index.xml": data["https://brave.com/blog/index.xml"]
    }
    fp = Aggregator(data, config.output_feed_path / "test.json")
    fp.report["feed_stats"] = {}
    entries = fp.get_rss()
    assert len(entries) != 0

    sorted_entries = sorted(entries, key=lambda entry: entry["publish_time"])
    sorted_entries.reverse()  # for most recent entries first

    assert sorted_entries


def test_scrub_html():
    with open(config.tests_data_dir / "test.json") as f:
        data = json.loads(f.read())
    data = {
        "https://brave.com/blog/index.xml": data["https://brave.com/blog/index.xml"]
    }
    fp = Aggregator(data, config.output_feed_path / "test.json")
    fp.report["feed_stats"] = {}
    entries = fp.get_rss()
    assert len(entries) != 0

    sorted_entries = sorted(entries, key=lambda entry: entry["publish_time"])
    sorted_entries.reverse()  # for most recent entries first

    filtered_entries = [scrub_html(i) for i in sorted_entries]

    assert filtered_entries


def test_score_entries():
    with open(config.tests_data_dir / "test.json") as f:
        data = json.loads(f.read())
    data = {
        "https://brave.com/blog/index.xml": data["https://brave.com/blog/index.xml"]
    }
    fp = Aggregator(data, config.output_feed_path / "test.json")
    fp.report["feed_stats"] = {}
    entries = fp.get_rss()
    assert len(entries) != 0

    sorted_entries = sorted(entries, key=lambda entry: entry["publish_time"])
    sorted_entries.reverse()  # for most recent entries first

    filtered_entries = [scrub_html(i) for i in sorted_entries]
    filtered_entries = score_entries(filtered_entries)

    assert filtered_entries
