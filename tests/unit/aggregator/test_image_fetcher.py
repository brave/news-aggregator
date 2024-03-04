from unittest.mock import Mock

import requests

from aggregator.image_fetcher import (
    check_images_in_item,
    check_small_image,
    get_article_img,
    process_image,
)


class TestProcessImage:
    # item has 'img' key
    def test_item_has_img_key(self):
        img_url = (
            "https://www.learningcontainer.com/wp-content/uploads/2020/08/"
            "Sample-Small-Image-PNG-file-Download.png"
        )
        item = (
            {"img": img_url},
            requests.get(img_url).content,
        )
        out_item = process_image(item)
        assert out_item["img"] is not None
        assert out_item["padded_img"] is not None

    # item has 'img' key but its value is None
    def test_item_img_value_is_none(self):
        item = ({"img": None}, None)
        out_item = process_image(item)
        assert out_item["img"] == ""
        assert out_item["padded_img"] == ""


class TestCheckSmallImage:
    def test_image_size_above_minimum(self, mocker):
        article = {"title": "Test Article", "img": "image_bytes"}
        img_bytes = b"image_bytes"
        is_large = False

        mocker.patch("PIL.Image.open").return_value.size = (500, 500)

        result = check_small_image((article, img_bytes, is_large))

        assert result == (article, img_bytes, is_large)

    def test_image_size_below_minimum(self, mocker):
        article = {"title": "Test Article", "img": "image_bytes"}
        img_bytes = b"image_bytes"
        is_large = False

        mocker.patch("PIL.Image.open").return_value.size = (200, 200)

        result = check_small_image((article, img_bytes, is_large))

        assert result[0]["img"] == ""

        assert result[1:] == (img_bytes, is_large)

    def test_image_open_error(self, mocker):
        article = {"title": "Test Article", "img": "image_bytes"}
        img_bytes = b"image_bytes"
        is_large = False

        mocker.patch("PIL.Image.open").side_effect = Exception("Image open error")

        result = check_small_image((article, img_bytes, is_large))

        assert result[0]["img"] == ""

        assert result[1:] == (img_bytes, is_large)


class TestCheckImagesInItem:
    def test_article_has_image_url(self, mocker):
        article_with_detail = (
            {
                "img": "https://example.com/image.jpg",
                "url": "https://example.com/article",
                "publisher_id": "28227a306c2ca84c4f2ea3c18836a07946b1692eaaed2f28dcab030221748a7d",
            },
            "content",
            True,
        )
        _publishers = {
            "28227a306c2ca84c4f2ea3c18836a07946b1692eaaed2f28dcab030221748a7d": {
                "og_images": True
            }
        }

        result = check_images_in_item(article_with_detail, _publishers)

        assert result == article_with_detail

    def test_malformed_or_invalid_url(self, mocker):
        mocker.patch(
            "metadata_parser.MetadataParser", side_effect=Exception("Invalid URL")
        )

        article_with_detail = ({"img": "", "url": "invalid_url"}, "content", True)
        _publishers = {"publisher_id": {"og_images": True}}

        result = check_images_in_item(article_with_detail, _publishers)

        assert result == article_with_detail

    def test_no_image_url_in_metadata(self, mocker):
        mocker.patch(
            "metadata_parser.MetadataParser",
            return_value=Mock(get_metadata_link=Mock(return_value=None)),
        )

        article_with_detail = (
            {"img": "", "url": "https://example.com/article"},
            "content",
            True,
        )
        _publishers = {"publisher_id": {"og_images": True}}

        result = check_images_in_item(article_with_detail, _publishers)

        assert result == article_with_detail


class TestGetArticleImg:
    def test_returns_image_url_from_image_key(self, mocker):
        article = {"image": "https://example.com/image.jpg"}
        mocker.patch("src.aggregator.image_fetcher.BS")
        result = get_article_img(article)
        assert result == "https://example.com/image.jpg"

    def test_returns_empty_string_if_image_key_is_empty(self, mocker):
        article = {"image": ""}
        mocker.patch("src.aggregator.image_fetcher.BS")
        result = get_article_img(article)
        assert result == ""

    def test_returns_empty_string_if_urlToImage_key_is_empty(self, mocker):
        article = {"urlToImage": ""}
        mocker.patch("src.aggregator.image_fetcher.BS")
        result = get_article_img(article)
        assert result == ""
