# Copyright (c) 2023 The Brave Authors. All rights reserved.
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at https://mozilla.org/MPL/2.0/. */

from io import BytesIO
from typing import Dict
from urllib.parse import urlparse

import metadata_parser
import structlog
from bs4 import BeautifulSoup as BS
from fake_useragent import UserAgent
from PIL import Image

import image_processor_sandboxed
from config import get_config

ua = UserAgent(browsers=["edge", "chrome", "firefox", "safari", "opera"])
config = get_config()
im_proc = image_processor_sandboxed.ImageProcessor(config.private_s3_bucket)
logger = structlog.getLogger(__name__)


def process_image(item: tuple) -> Dict[str, str]:
    out_item, content = item

    try:
        cache_fn = im_proc.cache_image(out_item.get("img"), content)
        if cache_fn:
            parsed_url = urlparse(cache_fn)
            out_item["padded_img"] = (
                cache_fn
                if parsed_url.scheme
                else f"{config.pcdn_url_base}/brave-today/cache/{cache_fn}"
            )
        else:
            out_item["img"] = ""
            out_item["padded_img"] = ""
    except Exception as e:
        # Handle the exception gracefully
        logger.error(f"Error processing image: {e}")
        out_item["img"] = ""
        out_item["padded_img"] = ""

    return out_item


def get_article_img(article: Dict) -> str:  # noqa: C901
    """
    Retrieves the image URL from the given article.

    Args:
        article Dict: The article object.

    Returns:
        str: The URL of the image.
    """
    image_url: str = ""

    if "image" in article:
        image_url = article["image"]
        if image_url:
            return image_url

    if "urlToImage" in article:
        image_url = article["urlToImage"]
        if image_url:
            return image_url

    if "media_content" in article:
        media = article.get("media_content")
        content_with_max_width = max(
            media, key=lambda content: int(content.get("width") or 0), default=None
        )
        if content_with_max_width:
            image_url = content_with_max_width.get("url")
            if image_url:
                return image_url

    if "summary" in article:
        soup = BS(article["summary"], features="html.parser")
        image_tags = soup.find_all("img")
        for img_tag in image_tags:
            if "src" in img_tag.attrs:
                image_url = img_tag["src"]
                break
        if image_url:
            return image_url

    if "content" in article:
        soup = BS(article["content"][0]["value"], features="html.parser")
        image_tags = soup.find_all("img")
        for img_tag in image_tags:
            if "src" in img_tag.attrs:
                image_url = img_tag["src"]
                break
        if image_url:
            return image_url

    return image_url


def check_images_in_item(article_with_detail, _publishers):  # noqa: C901
    """
    Check if the article has an image URL and if not, try to retrieve it from the metadata of the article's webpage.

    Args:
        article_with_detail (tuple): The dictionary representing the article.
        _publishers (dict): The dictionary representing the publishers.

    Returns:
        dict: The modified article dictionary with the updated image URL.
    """
    og_image = ""
    article, content, is_large = article_with_detail
    if not article.get("img") or _publishers[article["publisher_id"]]["og_images"]:
        try:
            page = metadata_parser.MetadataParser(
                url=article["url"],
                support_malformed=True,
                url_headers={"User-Agent": ua.random},
                search_head_only=True,
                strategy=["page", "meta", "og", "dc"],
                requests_timeout=config.request_timeout,
            )
            og_image = page.get_metadata_link("image") or ""
        except Exception as e:
            logger.error(f"Error parsing: {article['url']} -- {e}")

    if og_image:
        article["img"] = og_image

    article["padded_img"] = article["img"]

    return article, content, is_large


def check_small_image(article_with_bytes):
    article, img_bytes, is_large = article_with_bytes

    try:
        image = Image.open(BytesIO(img_bytes))
        if all(value < config.min_image_size for value in image.size):
            article["img"] = ""
    except Exception as e:
        logger.error(f"Error checking image size: {e}")
        article["img"] = ""

    return article, img_bytes, is_large
