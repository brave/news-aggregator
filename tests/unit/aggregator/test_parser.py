import pytest
from requests import HTTPError

from aggregator.parser import download_feed, get_with_max_size, parse_rss


class TestGetWithMaxSize:
    # Successfully retrieves content from a URL
    def test_retrieves_content(self):
        # Arrange
        url = "http://example.com"

        # Act
        result = get_with_max_size(url)

        # Assert
        assert result is not None
        assert isinstance(result, bytes)

    # Raises HTTPError for non-200 status codes
    def test_raises_http_error(self):
        # Arrange
        url = "http://example.com/nonexistent"

        # Act & Assert
        with pytest.raises(HTTPError):
            get_with_max_size(url)


class TestDownloadFeed:
    # Downloading a feed with a valid URL and default max_feed_size.
    def test_valid_url_default_max_feed_size(self):
        feed_url = "https://brave.com/blog/index.xml"
        result = download_feed(feed_url)
        assert result is not None
        assert "feed_cache" in result
        assert "key" in result

    # Downloading a feed with an invalid URL.
    def test_invalid_url(self):
        feed_url = "https://example.com/invalid_feed"
        result = download_feed(feed_url)
        assert result is None


class TestParseRss:
    # Successfully parse a downloaded RSS feed with at least one article.
    def test_parse_rss_success(self):
        downloaded_feed = {
            "key": "https://example.com/rss_feed",
            "feed_cache": "<rss version='2.0'><channel><title>Example Feed</title><item><title>Article 1"
            "</title></item></channel></rss>",
        }

        result = parse_rss(downloaded_feed)

        assert result is not None

    # Fail to parse a downloaded RSS feed with no articles.
    def test_parse_rss_failure(self):
        downloaded_feed = {
            "key": "https://example.com/rss_feed",
            "feed_cache": "<rss version='2.0'><channel><title>Example Feed</title></channel></rss>",
        }

        assert parse_rss(downloaded_feed) is None
