import hashlib
import logging
import os
import pathlib
import sys
import tempfile
from io import BytesIO

import boto3
import botocore
import cv2
import requests
from wasmer import engine, Store, Module, Instance
from wasmer_compiler_cranelift import Compiler

import config
from upload import upload_file

boto_session = boto3.Session()
s3_client = boto_session.client('s3')
s3_resource = boto3.resource('s3')

wasm_path = 'wasm_thumbnail.wasm'
wasm_store = Store(engine.JIT(Compiler))
# pylint: disable=consider-using-with
wasm_module = Module(wasm_store, open(wasm_path, 'rb').read())


def resize_and_pad_image(image_bytes, width, height, size, cache_path):
    pathlib.Path(os.path.dirname(cache_path)).mkdir(
        parents=True, exist_ok=True)
    pid = os.fork()
    if pid == 0:
        instance = Instance(wasm_module)

        image_length = len(image_bytes)
        input_pointer = instance.exports.allocate(image_length)
        memory = instance.exports.memory.uint8_view(input_pointer)
        memory[0:image_length] = image_bytes

        try:
            output_pointer = instance.exports.resize_and_pad(
                input_pointer, image_length, width, height, size)
        except RuntimeError:

            with tempfile.NamedTemporaryFile() as temp:
                temp.write(image_bytes)

                video_stream = cv2.VideoCapture(temp.name)
                image = video_stream.read()

                name = 'feed/image_from_video' + '.jpg'
                cv2.imwrite(name, image)

                with open(name, "rb") as image:

                    image_bytes = image.read()
                    image_length = len(image_bytes)
                    input_pointer = instance.exports.allocate(image_length)
                    memory = instance.exports.memory.uint8_view(input_pointer)
                    memory[0:image_length] = image_bytes

                    output_pointer = instance.exports.resize_and_pad(
                        input_pointer, image_length, width, height, size)

        except Exception:
            logging.warning("resize_and_pad() hit a RuntimeError (length=%s, width=%s, height=%s, size=%s): %s.failed",
                            image_length, width, height, size, cache_path)
            with open(f'{cache_path}.failed', 'wb+', encoding="utf-8") as out_image:
                out_image.write(image_bytes)
            sys.exit(1)

        memory = instance.exports.memory.uint8_view(output_pointer)
        out_bytes = bytes(memory[:size])
        with open(f'{cache_path}.pad', 'wb+', encoding="utf-8") as out_image:
            out_image.write(out_bytes)
        sys.exit(0)

    pid, status = os.waitpid(pid, 0)

    if status == 0:
        return True
    return False


def get_with_max_size(url, max_bytes):
    response = requests.get(url, stream=True, timeout=10)
    response.raise_for_status()
    if response.headers.get('Content-Length') and int(response.headers.get('Content-Length')) > max_bytes:
        raise ValueError('Content-type too large')
    count = 0
    content = BytesIO()
    for chunk in response.iter_content(4096):
        count += len(chunk)
        content.write(chunk)
        if count > max_bytes:
            raise ValueError('Received more than max_bytes')
    return content.getvalue()


class ImageProcessor():
    def __init__(self, s3_bucket=None):
        self.s3_bucket = s3_bucket

    def cache_image(self, url):
        cache_fn = f'{hashlib.sha256(url.encode("utf-8")).hexdigest()}.jpg'
        cache_path = f'./feed/cache/{cache_fn}'

        # if we have it dont do it again
        if os.path.isfile(cache_path):
            return cache_fn
        # also check if we have it on s3
        if not config.NO_UPLOAD:
            exists = False
            try:
                s3_resource.Object(
                    self.s3_bucket, f'brave-today/cache/{cache_fn}.pad').load()
                exists = True
            except ValueError:
                exists = False  # make tests work
            except botocore.exceptions.ClientError as e:
                if e.response['Error']['Code'] == "404":
                    exists = False
                else:
                    return None  # should retry
            if exists:
                return cache_fn

        try:
            content = get_with_max_size(url, 5000000)  # 5mb max
        except requests.exceptions.ReadTimeout:
            return None
        except ValueError:
            return None  # skipping (image exceeds maximum size)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code not in (403, 429, 500, 502, 503):
                logging.error(
                    "Failed to get image [%s]: %s", e.response.status_code, url)
            return None

        if not resize_and_pad_image(content, 1168, 657, 250000, cache_path):
            logging.error("Failed to cache image %s", url)
            return None

        if self.s3_bucket and not config.NO_UPLOAD:
            upload_file(f'feed/cache/{cache_fn}.pad',
                        self.s3_bucket, f'brave-today/cache/{cache_fn}.pad')
        return cache_fn
