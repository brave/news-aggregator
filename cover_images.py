import json
import os
import urllib
from multiprocessing import Pool
from typing import Tuple, List, Optional

import requests
from PIL import Image
from bs4 import BeautifulSoup
from structlog import get_logger

import config
import image_processor_sandboxed
from color import color_length, hex_color, is_transparent
from utils import get_all_domains, ensure_scheme, upload_file

# In seconds. Tested with 5s but it's too low for a bunch of sites
REQUEST_TIMEOUT = 15

CACHE_FOLDER = '.cache'
logger = get_logger()
im_proc = image_processor_sandboxed.ImageProcessor(config.PRIV_S3_BUCKET, s3_path='brave-today/cover_images/{}.pad',
                                                   force_upload=True)

os.makedirs(CACHE_FOLDER, exist_ok=True)


def get_soup(domain) -> Optional[BeautifulSoup]:
    try:
        html = requests.get(domain, timeout=REQUEST_TIMEOUT, headers={
            "user-agent": config.USER_AGENT}).content.decode('utf-8')
        return BeautifulSoup(html, features='lxml')
    # Failed to download html
    except:
        return None


def get_manifest_icon_urls(site_url: str, soup: BeautifulSoup):
    manifest_rel = soup.select_one('link[rel="manifest"]')
    if not manifest_rel: return []

    manifest_link = manifest_rel.attrs['href']
    if not manifest_link: return []

    url = urllib.parse.urljoin(site_url, manifest_link)

    try:
        manifest_response = requests.get(url, timeout=REQUEST_TIMEOUT, headers={"user-agent": config.USER_AGENT})

        if not manifest_response.ok:
            logger.info(f'Failed to download manifest from {url}')
            return []

        content = manifest_response.content.decode('utf-8')
        manifest_json = json.loads(content)

        if 'icons' not in manifest_json:
            return []

        for icon_raw in manifest_json['icons']:
            if 'src' not in icon_raw:
                continue
            yield icon_raw['src']
    except:
        return []


def get_apple_icon_urls(site_url: str, soup: BeautifulSoup):
    image_rels = soup.select('link[rel="apple-touch-icon"]')
    image_rels += soup.select('link[rel="icon"]')

    for rel in image_rels:
        if not rel.has_attr('href'):
            continue
        yield rel.attrs['href']


def get_open_graph_icon_urls(site_url: str, soup: BeautifulSoup):
    image_metas = soup.select('meta[property="og:image"]')
    image_metas += soup.select('meta[property="twitter:image"]')
    image_metas += soup.select('meta[property="image"]')

    for meta in image_metas:
        if not meta.has_attr('content'):
            continue
        yield meta.attrs['content']


def get_filename(url: str):
    return os.path.join(CACHE_FOLDER, urllib.parse.quote_plus(url))


def get_icon(icon_url: str) -> Image:
    filename = get_filename(icon_url)
    if filename.endswith('.svg') or filename.endswith('.ico'):
        # Can't handle SVGs or favicons
        return None

    try:
        if not os.path.exists(filename):
            response = requests.get(icon_url, stream=True, timeout=REQUEST_TIMEOUT,
                                    headers={"user-agent": config.USER_AGENT})
            if not response.ok:
                return None

            with open(filename, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)

        return Image.open(filename).convert('RGBA')

    # Failed to download the image, or the thing we downloaded wasn't valid.
    except:
        return None


def get_best_image(site_url: str) -> tuple[Image, str]:
    sources = [get_manifest_icon_urls, get_apple_icon_urls, get_open_graph_icon_urls]

    soup = get_soup(site_url)
    if not soup:
        return None

    # The sources are in preference order. We take the largest image, if any
    # If a source has no images, we fall through to the next one.
    for source in sources:
        icon_urls = [urllib.parse.urljoin(site_url, url) for url in source(site_url, soup)]
        icons = filter(lambda x: x[0] is not None, [(get_icon(url), url) for url in icon_urls])
        icons = list(reversed(sorted(icons, key=lambda x: min(x[0].size))))
        if len(icons) != 0:
            return icons[0]


def find_non_transparent(image: Image, start: Tuple[int, int], step: Tuple[int, int], min_transparency=0.8):
    width, height = image.size
    x, y = start
    step_x, step_y = step

    while True:
        color = image.getpixel((x, y))
        if not is_transparent(color, min_transparency): return color

        x += step_x
        y += step_y

        if x < 0 or y < 0 or x >= width or y >= height:
            return None


def get_background_color(image: Image):
    """
    After a bunch of experimentation we found the best way
    of determining the background color of an icon to be to take
    the median edge color. That is, the middle most color of all
    the edge pixels in the image.
    """
    width, height = image.size
    colors = []

    # add all the vertical edge pixels
    for y in range(height):
        left = find_non_transparent(image, (0, y), (1, 0))
        right = find_non_transparent(image, (width - 1, y), (-1, 0))

        colors.append(left)
        colors.append(right)

    # add all the horizontal edge pixels
    for x in range(width):
        top = find_non_transparent(image, (x, 0), (0, 1))
        bottom = find_non_transparent(image, (x, height - 1), (0, -1))

        colors.append(top)
        colors.append(bottom)

    colors = [color for color in colors if color is not None]
    if len(colors) == 0:
        return None

    colors.sort(key=color_length)
    color = colors[len(colors) // 2]
    return hex_color(color)


def process_site(domain: str):
    domain = ensure_scheme(domain)

    result = get_best_image(domain)
    if not result:
        return None

    image, image_url = result
    background_color = get_background_color(image) if image is not None else None

    return domain, image_url, background_color


def process_cover_image(item):
    domain = ""
    image_url = ""
    padded_image_url = ""
    background_color = ""
    try:
        domain, image_url, background_color = item
        try:
            cache_fn = im_proc.cache_image(image_url)
        except Exception as e:
            cache_fn = None
            logger.error(f"im_proc.cache_image failed [e]: {image_url}")
        if cache_fn:
            if cache_fn.startswith("https"):
                padded_image_url = cache_fn
            else:
                padded_image_url = f"{config.PCDN_URL_BASE}/brave-today/cover_images/{cache_fn}.pad"
        else:
            padded_image_url = ""

    except ValueError as e:
        logger.info(f"Tuple unpacking error {e}")

    if padded_image_url:
        return domain, padded_image_url, background_color
    else:
        return domain, image_url, background_color


if __name__ == '__main__':
    domains = list(set(get_all_domains()))[:]
    logger.info(f'Processing {len(domains)} domains')

    cover_infos: List[Tuple[str, str, str]]

    # This work is IO bound, so it's okay to start up a bunch more threads
    # than we have cores, it just means we'll have more in flight requests.
    with Pool(100) as p:
        cover_infos = list(filter(lambda x: x is not None, p.map(process_site, domains)))

    processed_cover_images: List[Tuple[str, str, str]]
    with Pool(config.CONCURRENCY) as pool:
        processed_cover_images = pool.map(process_cover_image, cover_infos)

    result = {}
    for entry in processed_cover_images:
        result.update({
            entry[0]: {
                'cover_url': entry[1],
                'background_color': entry[2]
            }
        })

    with open('cover_info_lookup.json', 'w') as f:
        f.write(json.dumps(result, indent=4))

    logger.info("Fetched all the Cover images!")

    if not config.NO_UPLOAD:
        upload_file(f"{config.COVER_INFO_LOOKUP_FILE}.json", config.PUB_S3_BUCKET,
                    f"{config.COVER_INFO_LOOKUP_FILE}.json")
        logger.info(f"{config.COVER_INFO_LOOKUP_FILE} is upload to S3")
