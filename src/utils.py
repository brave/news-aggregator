# Copyright (c) 2023 The Brave Authors. All rights reserved.
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at https://mozilla.org/MPL/2.0/. */

import logging
import mimetypes
import re
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import boto3
import orjson
import structlog
from botocore.exceptions import ClientError
from prometheus_client import push_to_gateway

import config

boto_session = boto3.Session()
s3_client = boto_session.client("s3")

domain_url_fixer = re.compile(r"^https://(www\.)?|^")
subst = "https://www."

config = config.get_config()

logger = structlog.getLogger(__name__)


class InvalidS3Bucket(Exception):
    pass


class ObjectNotFound(Exception):
    pass


class ExpiredRegions(Exception):
    def __init__(self, message):
        super().__init__(message)


def upload_file(file_name: Path, bucket: str, object_name: Optional[str] = None):
    if object_name is None:
        object_name = file_name
    try:
        content_type = mimetypes.guess_type(file_name)[0] or "binary/octet-stream"
        if bucket == config.pub_s3_bucket:
            s3_client.upload_file(
                file_name,
                bucket,
                object_name,
                ExtraArgs={
                    "GrantRead": "id=%s" % config.brave_today_cloudfront_canonical_id,
                    "GrantFullControl": "id=%s" % config.brave_today_canonical_id,
                    "ContentType": content_type,
                },
            )
        elif bucket == config.private_s3_bucket:
            s3_client.upload_file(
                file_name,
                bucket,
                object_name,
                ExtraArgs={
                    "GrantRead": "id=%s" % config.private_cdn_canonical_id,
                    "GrantFullControl": "id=%s"
                    % config.private_cdn_cloudfront_canonical_id,
                    "ContentType": content_type,
                },
            )
        else:
            raise InvalidS3Bucket("Attempted to upload to unknown S3 bucket.")

    except ClientError as e:
        logging.error(e)
        return False
    return True


def download_file(file_name: str, bucket: str, object_name: Optional[str] = None):
    if object_name is None:
        object_name = file_name

    try:
        if bucket == config.pub_s3_bucket:
            s3_client.download_file(bucket, object_name, file_name)
        elif bucket == config.private_s3_bucket:
            s3_client.download_file(bucket, object_name, file_name)
        else:
            raise InvalidS3Bucket("Attempted to upload to unknown S3 bucket.")

    except ClientError as e:
        logging.error(e)
        return False
    return True


def ensure_scheme(domain):
    """Helper utility for ensuring a domain has a scheme. If none is attached
    this will use the https scheme.

    Note: this will break if domain has a non http(s) scheme.
    example.com ==> https://www.example.com
    https://example.com ==> https://www.example.com
    file://example.com ==> https://file://example.com
    """
    return domain_url_fixer.sub(subst, domain, 1)


def get_all_domains() -> List[str]:
    """Helper utility for getting all domains across all sources"""
    source_files = list(config.sources_dir.glob("sources.*_*.csv"))
    for source_file in source_files:
        with open(source_file) as f:
            # Skip the first line, with the headers.
            lines = f.readlines()[1:]

            # The domain is the first field on the line
            yield from [line.split(",")[0].strip() for line in lines]


def uri_validator(x):
    """
    'http://www.cwi.nl:80/%7Eguido/Python.html' False
    '/data/Python.html' False
    '532' False
    u'dkakasdkjdjakdjadjfalskdjfalk' False
    'https://stackoverflow.com' True

    :param x: URL
    :return: bool
    """
    try:
        result = urlparse(x)
        return all([result.scheme, result.scheme == "https", result.netloc])
    except Exception:
        return False


def get_favicons_lookup() -> Dict[Any, Any]:
    if not config.no_download:
        download_file(
            str(config.output_path / config.favicon_lookup_file),
            config.pub_s3_bucket,
            str(config.favicon_lookup_file),
        )

    if Path(config.output_path / config.favicon_lookup_file).is_file():
        with open(config.output_path / config.favicon_lookup_file) as f:
            favicons_lookup = orjson.loads(f.read())
            return favicons_lookup
    else:
        return {}


def get_cover_infos_lookup() -> Dict[Any, Any]:
    if not config.no_download:
        download_file(
            str(config.output_path / config.cover_info_lookup_file),
            config.pub_s3_bucket,
            str(config.cover_info_lookup_file),
        )

    if Path(config.output_path / config.cover_info_lookup_file).is_file():
        with open(config.output_path / config.cover_info_lookup_file) as f:
            cover_infos_lookup = orjson.loads(f.read())
            return cover_infos_lookup
    else:
        return {}


def push_metrics_to_pushgateway(metric, metric_value, label_value, registry):
    try:
        # Set the metric value
        metric.labels(url=label_value).inc(metric_value)

        # Push the metrics to the Pushgateway
        push_to_gateway(
            config.prom_pushgateway_url, job="news-aggregator", registry=registry
        )

    except Exception as e:
        logger.error(f"Failed to push metrics: {e}")


def perform_overrides(result, domain_overrides):
    logger.info("replacing cover image and background color for domains in the domain_overrides table")
    for override in domain_overrides:
        # check to see if the domain is in the result
        if result.get(override[0]):
            if override[1] == "background_color":
                logger.info(f"replacing background color for {override[0]}")
                result[override[0]]["background_color"] = override[2]
            elif override[1] == "cover_url":
                logger.info(f"replacing cover url for {override[0]}")
                result[override[0]]["cover_url"] = override[2]

    return result