# Copyright (c) 2023 The Brave Authors. All rights reserved.
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at https://mozilla.org/MPL/2.0/. */

import hashlib
import os
import struct

import boto3
import requests
import structlog
from fake_useragent import UserAgent
from wasmer import Instance, Module, Store, engine
from wasmer_compiler_cranelift import Compiler

from config import get_config
from utils import upload_file

ua = UserAgent(browsers=["edge", "chrome", "firefox", "safari", "opera"])

config = get_config()

logger = structlog.getLogger(__name__)

boto_session = boto3.Session()
s3_client = boto_session.client("s3")
s3_resource = boto3.resource("s3")

wasm_store = Store(engine.JIT(Compiler))
wasm_module = Module(wasm_store, open(config.wasm_thumbnail_path, "rb").read())
instance = Instance(wasm_module)


def get_unpadded_length(data):
    """Get the unpadded length from the header."""
    data_length_without_header = len(data) - 4
    if data_length_without_header < 0:
        raise ValueError("Data must be at least 4 bytes long", len(data))

    return struct.unpack("!L", data[0:4])[0]


def resize_and_pad_image(image_bytes, width, height, size, cache_path, quality=80):
    """
    Resizes and pads an image.

    Args:
        image_bytes (bytes): The bytes of the image to resize and pad.
        width (int): The desired width of the image.
        height (int): The desired height of the image.
        size (int): The size of the output image.
        cache_path (str): The path where the resized and padded image will be cached.
        quality (int, optional): The quality of the resized image. Defaults to 80.

    Returns:
        bool: True if the image was successfully resized and padded, False otherwise.
    """
    image_length = len(image_bytes)
    input_pointer = instance.exports.allocate(image_length)
    memory = instance.exports.memory.uint8_view(input_pointer)
    memory[0:image_length] = image_bytes

    try:
        output_pointer = instance.exports.resize_and_pad(
            input_pointer, image_length, width, height, size, quality
        )
        instance.exports.deallocate(input_pointer, image_length)

        memory = instance.exports.memory.uint8_view(output_pointer)
        out_bytes = bytes(memory[:size])

        instance.exports.deallocate(output_pointer, size)

        unpadded_length = get_unpadded_length(out_bytes)
        if unpadded_length == 0:
            raise RuntimeError("Image resizing failed")

        with open(str(cache_path), "wb+") as out_image:
            out_image.write(out_bytes)

        return True
    except RuntimeError:
        logger.info(
            f"resize_and_pad() hit a RuntimeError "
            f"(length={image_length}, width={width}, height={height}, size={size}): {cache_path}.failed"
        )

        return False


def get_with_max_size(url, max_bytes=1000000):
    """
    Retrieves the content of a URL and checks if it exceeds a maximum size.

    Args:
        url (str): The URL to retrieve the content from.
        max_bytes (int, optional): The maximum size in bytes allowed for the content. Defaults to 1000000.

    Returns:
        tuple: A tuple containing the content of the response as bytes and a boolean indicating if the content
        is larger than the maximum size.
    """
    is_large = False
    response = requests.get(
        url,
        timeout=config.request_timeout,
        headers={"User-Agent": ua.random, **config.default_headers},
    )
    response.raise_for_status()
    if (
        response.headers.get("Content-Length")
        and int(response.headers.get("Content-Length")) > max_bytes
    ):
        is_large = True

    return response.content, is_large


class ImageProcessor:
    def __init__(
        self,
        s3_bucket=None,
        s3_path="brave-today/cache/{}",
        force_upload=False,
        img_format="jpg",
        img_width=900,
        img_height=750,
        img_size=1000000,
    ):
        self.s3_bucket = s3_bucket
        self.s3_path = s3_path
        self.force_upload = force_upload
        self.img_format = img_format
        self.img_width = img_width
        self.img_height = img_height
        self.img_size = img_size

    def cache_image(self, url):  # noqa: C901
        """
        Caches an image from a given URL.

        Args:
            url (str): The URL of the image to be cached.

        Returns:
            str: The filename of the cached image, or None if caching failed.
        """
        content = None
        cache_path = None
        cache_fn = None

        try:
            content, is_large = get_with_max_size(url)  # 1mb max
            if not is_large and not self.force_upload:
                return url

            cache_fn = f"{hashlib.sha256(url.encode('utf-8')).hexdigest()}.{self.img_format}.pad"
            cache_path = config.img_cache_path / cache_fn

            # if we have it don't do it again
            if os.path.isfile(cache_path):
                return cache_fn
            # also check if we have it on s3
            if not config.no_upload:
                try:
                    s3_resource.Object(
                        self.s3_bucket, self.s3_path.format(cache_fn)
                    ).load()
                    exists = True
                except Exception:
                    exists = False
                if exists:
                    return cache_fn
        except Exception as e:
            logger.info(f"Image is not already uploaded {url} with {e}")

        if not resize_and_pad_image(
            content,
            self.img_width,
            self.img_height,
            self.img_size,
            str(cache_path),
        ):
            logger.info(f"Failed to cache image {url}")
            return None

        if self.s3_bucket and not config.no_upload:
            upload_file(
                cache_path,
                self.s3_bucket,
                self.s3_path.format(cache_fn),
            )
        return cache_fn
