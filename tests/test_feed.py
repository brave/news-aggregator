from feed import (
    get_article_img,
)

class TestGetArticleImg:
    def test_image(self):
        # Arrange
        article = {
            "image": "https://example.com/image.jpg",
        }

        # Act
        url = get_article_img(article)

        # Assert
        assert url == "https://example.com/image.jpg", "Should return the image URL"

    def testUrlToImage(self):
        # Arrange
        article = {
            "urlToImage": "https://example.com/urlToImg.jpg",
        }

        # Act
        url = get_article_img(article)

        # Assert
        assert url == "https://example.com/urlToImg.jpg", "Should return the image URL"

    def test_media_content_media_content(self):
        # Arrange
        article = {
            "media_content": [
                {
                    "url": "https://example.com/media_content.jpg",
                    "width": "100",
                },
                {
                    "url": "https://example.com/media_content2.jpg",
                    "width": "200",
                },
            ],
        }

        # Act
        url = get_article_img(article)

        # Assert
        assert url == "https://example.com/media_content2.jpg", "Should return the image URL"

    def test_media_thumbnail_media_thumbnail(self):
        # Arrange
        article = {
            "media_thumbnail": [
                {
                    "url": "https://example.com/media_thumbnail.jpg",
                    "width": "100",
                },
                {
                    "url": "https://example.com/media_thumbnail2.jpg",
                    "width": "200",
                },
            ],
        }

        # Act
        url = get_article_img(article)

        # Assert
        assert url == "https://example.com/media_thumbnail2.jpg", "Should return the image URL"

    def test_summary(self):
        # Arrange
        article = {
            "summary": "<html><body><img src='https://example.com/summary.jpg'></body></html>",
        }

        # Act
        url = get_article_img(article)

        # Assert
        assert url == "https://example.com/summary.jpg", "Should return the image URL"

    def test_summary_content(self):
        # Arrange
        article = {
            "content": [
                {
                    "value": "<html><body><img src='https://example.com/content.jpg'></body></html>",
                },
            ],
        }

        # Act
        url = get_article_img(article)

        # Assert
        assert url == "https://example.com/content.jpg", "Should return the image URL"

    def test_summary_content_no_img(self):
        # Arrange
        article = {
            "content": [
                {
                    "value": "<html><body></body></html>",
                },
            ],
        }

        # Act
        url = get_article_img(article)

        # Assert
        assert url == "", "Should return the empty string"