import hashlib
from datetime import datetime

import pytz

from aggregator.processor import process_articles, scrub_html, unshorten_url


class TestProcessArticles:
    # Process a valid article with all required fields.

    def test_valid_article_with_required_fields(
        self,
        fake_date=datetime.now().replace(tzinfo=pytz.utc).strftime("%Y-%m-%d"),
    ):
        article = {
            "title": "Example Article",
            "link": "https://www.example.com/article",
            "updated": fake_date,
            "description": "This is an example article",
            "publisher_id": "example_publisher",
            "publisher_name": "Example Publisher",
            "creative_instance_id": "example_creative_instance",
            "category": "example_category",
            "content_type": "text",
        }

        _publisher = {
            "publisher_id": "example_publisher",
            "publisher_name": "Example Publisher",
            "creative_instance_id": "example_creative_instance",
            "category": "example_category",
            "content_type": "text",
            "channels": ["Top News"],
            "site_url": "https://brave.com/",
        }

        processed_article = process_articles(article, _publisher)

        assert processed_article is not None
        assert processed_article["title"] == "Example Article"
        assert processed_article["link"] == "https://www.example.com/article"
        assert processed_article["img"] == ""
        assert processed_article["category"] == "example_category"
        assert processed_article["description"] == "This is an example article"
        assert processed_article["content_type"] == "text"
        assert processed_article["publisher_id"] == "example_publisher"
        assert processed_article["publisher_name"] == "Example Publisher"
        assert processed_article["creative_instance_id"] == "example_creative_instance"
        assert processed_article["channels"] == ["Top News"]

    # Skip processing an article with no title.
    def test_skip_article_with_no_title(self):
        article = {
            "link": "https://www.example.com/article",
            "updated": "2022-01-01T12:00:00Z",
            "description": "This is an example article",
            "publisher_id": "example_publisher",
            "publisher_name": "Example Publisher",
            "creative_instance_id": "example_creative_instance",
            "category": "example_category",
            "content_type": "text",
        }

        _publisher = {
            "publisher_id": "example_publisher",
            "publisher_name": "Example Publisher",
            "creative_instance_id": "example_creative_instance",
            "category": "example_category",
            "content_type": "text",
        }

        processed_article = process_articles(article, _publisher)

        assert processed_article is None

    # Skip processing an article with a profanity in the title.
    def test_skip_article_with_profanity_in_title(self, mocker):
        mocker.patch("better_profanity.profanity.contains_profanity", return_value=True)

        article = {
            "title": "Example Article with profanity",
            "link": "https://www.example.com/article",
            "updated": "2022-01-01T12:00:00Z",
            "description": "This is an example article",
            "publisher_id": "example_publisher",
            "publisher_name": "Example Publisher",
            "creative_instance_id": "example_creative_instance",
            "category": "example_category",
            "content_type": "text",
        }

        _publisher = {
            "publisher_id": "example_publisher",
            "publisher_name": "Example Publisher",
            "creative_instance_id": "example_creative_instance",
            "category": "example_category",
            "content_type": "text",
        }

        processed_article = process_articles(article, _publisher)

        assert processed_article is None


class TestUnshortenUrl:
    # Unshortens a valid URL.
    def test_unshorten_valid_url(self, mocker):
        # Mock the unshortener object
        mock_unshortener = mocker.Mock()
        mocker.patch("unshortenit.UnshortenIt", return_value=mock_unshortener)

        # Mock the unshorten method
        mock_unshortener.unshorten.return_value = "https://example.com"

        # Create the input article
        out_article = {
            "link": "https://bit.ly/3i2QJgA",
            "title": "Example Article",
            "author": "John Doe",
        }

        # Call the function under test
        result = unshorten_url(out_article)

        # Assert the unshortened URL is correct
        assert result["url"] == "https://example.com"

        # Assert the link key is removed
        assert "link" not in result

        # Assert the URL hash is correct
        assert (
            result["url_hash"]
            == hashlib.sha256("https://example.com".encode("utf-8")).hexdigest()
        )

        # Assert the URL is encoded
        assert result["url"] == "https://example.com"

    # Skips unshortening if the URL is None.
    def test_skip_unshortening_if_url_none(self, mocker):
        # Create the input article with None URL
        out_article = {"link": None, "title": "Example Article", "author": "John Doe"}

        # Call the function under test
        result = unshorten_url(out_article)

        # Assert the result is None
        assert result is None


class TestScrubHtml:
    # Scrubs HTML content in a dictionary with valid HTML tags and attributes.
    def test_valid_html_tags_and_attributes(self):
        feed = {
            "title": "<h1>This is a title</h1>",
            "description": "<p>This is a description</p>",
            "content": "<div>This is some content</div>",
        }

        scrubbed_feed = scrub_html(feed)

        assert scrubbed_feed["title"] == "This is a title"
        assert scrubbed_feed["description"] == "This is a description"
        assert scrubbed_feed["content"] == "This is some content"

    # Scrubs HTML content in a dictionary with invalid HTML tags and attributes.
    def test_invalid_html_tags_and_attributes(self):
        feed = {
            "title": "<h1>This is a title</h1>",
            "description": "<p>This is a description</p>",
            "content": "<script>alert('Hello World!')</script>",
        }

        scrubbed_feed = scrub_html(feed)

        assert scrubbed_feed["title"] == "This is a title"
        assert scrubbed_feed["description"] == "This is a description"
        assert scrubbed_feed["content"] == "alert('Hello World!')"
