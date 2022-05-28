import json
import os

import feedparser

import feed_processor_multi


# def test_image_processor():
#     im_proc = image_processor_sandboxed.ImageProcessor()
#     result = im_proc.cache_image('https://brave.com/wp-content/uploads/2019/03/brave-logo.png')
#     assert result
#     assert os.stat("feed/cache/%s.pad" % (result)).st_size != 0

def test_feed_processor_download():
    result = feed_processor_multi.download_feed(
        'https://brave.com/blog/index.xml')
    assert result


def test_feed_processor_aggregate():
    fp = feed_processor_multi.FeedProcessor()
    with open('test.json', encoding="utf-8") as f:
        feeds = json.loads(f.read())
        fp.aggregate(feeds, "feed/test.json")
    assert os.stat("feed/test.json").st_size != 0

    with open('feed/test.json', encoding="utf-8") as f:
        data = json.loads(f.read())
    assert data
    assert len(data) != 0


def test_check_images():
    data = [feedparser.parse('test.rss')['items'][0]]
    data[0]['img'] = data[0]['media_content'][0]['url']
    data[0]['publisher_id'] = ""
    fp = feed_processor_multi.FeedProcessor()
    fp.feeds[""] = {'og_images': False}
    assert fp.check_images(data)


def test_download_feeds():
    fp = feed_processor_multi.FeedProcessor()
    with open('test.json', encoding="utf-8") as f:
        data = json.loads(f.read())
    data = {
        'https://brave.com/blog/index.xml': data['https://brave.com/blog/index.xml']}
    fp.report['feed_stats'] = {}
    result = fp.download_feeds(data)
    assert len(result) != 0


def test_get_rss():
    fp = feed_processor_multi.FeedProcessor()
    with open('test.json', encoding="utf-8") as f:
        data = json.loads(f.read())
    data = {
        'https://brave.com/blog/index.xml': data['https://brave.com/blog/index.xml']}
    fp.report['feed_stats'] = {}
    result = fp.get_rss(data)
    assert len(result) != 0


def test_fixup_entries():
    fp = feed_processor_multi.FeedProcessor()
    with open('test.json', encoding="utf-8") as f:
        data = json.loads(f.read())
    data = {
        'https://brave.com/blog/index.xml': data['https://brave.com/blog/index.xml']}
    fp.report['feed_stats'] = {}
    entries = fp.get_rss(data)
    assert len(entries) != 0

    sorted_entries = sorted(entries, key=lambda entry: entry["publish_time"])
    sorted_entries.reverse()  # for most recent entries first

    filtered_entries = fp.fixup_entries(sorted_entries)
    assert filtered_entries


def test_scrub_html():
    fp = feed_processor_multi.FeedProcessor()
    with open('test.json', encoding="utf-8") as f:
        data = json.loads(f.read())
    data = {
        'https://brave.com/blog/index.xml': data['https://brave.com/blog/index.xml']}
    fp.report['feed_stats'] = {}
    entries = fp.get_rss(data)
    assert len(entries) != 0

    sorted_entries = sorted(entries, key=lambda entry: entry["publish_time"])
    sorted_entries.reverse()  # for most recent entries first

    filtered_entries = fp.fixup_entries(sorted_entries)
    filtered_entries = fp.scrub_html(filtered_entries)

    assert filtered_entries


def test_score_entries():
    fp = feed_processor_multi.FeedProcessor()
    with open('test.json', encoding="utf-8") as f:
        data = json.loads(f.read())
    data = {
        'https://brave.com/blog/index.xml': data['https://brave.com/blog/index.xml']}
    fp.report['feed_stats'] = {}
    entries = fp.get_rss(data)
    assert len(entries) != 0

    sorted_entries = sorted(entries, key=lambda entry: entry["publish_time"])
    sorted_entries.reverse()  # for most recent entries first

    filtered_entries = fp.fixup_entries(sorted_entries)
    filtered_entries = fp.scrub_html(filtered_entries)
    filtered_entries = fp.score_entries(filtered_entries)

    assert filtered_entries
