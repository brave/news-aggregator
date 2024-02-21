import requests

from aggregator.image_fetcher import check_small_image, process_image


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
