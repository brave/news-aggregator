from typing import Dict
from bs4 import BeautifulSoup as BS

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

    elif "urlToImage" in article:
        image_url = article["urlToImage"]

    elif "media_content" in article or "media_thumbnail" in article:
        media = article.get("media_content") or article.get("media_thumbnail")
        content_with_max_width = max(
            media, key=lambda content: int(content.get("width") or 0), default=None
        )
        if content_with_max_width:
            image_url = content_with_max_width.get("url")

    elif "summary" in article:
        soup = BS(article["summary"], features="html.parser")
        image_tags = soup.find_all("img")
        for img_tag in image_tags:
            if "src" in img_tag.attrs:
                image_url = img_tag["src"]
                break

    elif "content" in article:
        soup = BS(article["content"][0]["value"], features="html.parser")
        image_tags = soup.find_all("img")
        for img_tag in image_tags:
            if "src" in img_tag.attrs:
                image_url = img_tag["src"]
                break

    return image_url