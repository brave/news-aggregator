# Copyright (c) 2023 The Brave Authors. All rights reserved.
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at https://mozilla.org/MPL/2.0/. */

import logging
import os
from functools import lru_cache
from multiprocessing import cpu_count
from pathlib import Path
from typing import Optional

import structlog
from pydantic import BaseSettings, Field, validator
from pytz import timezone

logger = structlog.getLogger(__name__)


class Configuration(BaseSettings):
    user_agent: str = (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"
    )

    tz = timezone("UTC")
    request_timeout = 30

    output_feed_path: Path = Field(default=Path(__file__).parent / "output/feed")
    output_path: Path = Field(default=Path(__file__).parent / "output")
    wasm_thumbnail_path: Path = Field(
        default=Path(__file__).parent / "wasm_thumbnail.wasm"
    )
    img_cache_path: Path = Field(default=Path(__file__).parent / "output/feed/cache")

    # Set the number of processes to spawn for all multiprocessing tasks.
    concurrency = cpu_count()
    thread_pool_size = cpu_count() * 10

    # Disable uploads and downloads to S3. Useful when running locally or in CI.
    no_upload: Optional[str] = None
    no_download: Optional[str] = None

    # Database configuration
    db_host: str = "localhost"
    db_name: str = "news"

    # enabled domain overrides for background colors and cover images
    domain_overrides: Optional[str] = None

    pcdn_url_base: str = Field(default="https://pcdn.brave.software")

    # Canonical ID of the private S3 bucket
    private_s3_bucket: str = Field(default="brave-private-cdn-development")
    private_cdn_canonical_id: str = ""
    private_cdn_cloudfront_canonical_id: str = ""

    # Canonical ID of the public S3 bucket
    pub_s3_bucket: str = Field(default="brave-today-cdn-development")
    brave_today_canonical_id: str = ""
    brave_today_cloudfront_canonical_id: str = ""

    sources_file: Path = Field(default="sources")
    sources_dir: Path = Field(default=Path(__file__).parent / "sources")
    global_sources_file: Path = Field(default="sources.global.json")
    favicon_lookup_file: Path = Field(default="favicon_lookup.json")
    cover_info_lookup_file: Path = Field(default="cover_info_lookup.json")
    cover_info_cache_dir: Path = Field(default="cover_info_cache")
    tests_dir: Path = Field(default=Path(__file__).parent / "tests")

    sentry_url: str = ""

    log_level: str = "info"


    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.getLevelName(log_level.upper())
        ),
    )

    if sentry_url:
        import sentry_sdk

        sentry_sdk.init(dsn=sentry_url, traces_sample_rate=0)

    prom_pushgateway_url: Optional[str] = None

    prometheus_multiproc_dir: Path = Field(
        default=Path(__file__).parent / "output/prom_tmp"
    )

    bs_pop_endpoint: str = ""

    nu_api_url: str = ""
    nu_api_token: str = ""

    @validator("img_cache_path")
    def create_img_cache_path(cls, v: Path) -> Path:
        v.mkdir(parents=True, exist_ok=True)
        return v

    @validator("prometheus_multiproc_dir")
    def create_prometheus_multiproc_dir(cls, v: Path) -> Path:
        v.mkdir(parents=True, exist_ok=True)
        os.environ["PROMETHEUS_MULTIPROC_DIR"] = str(v)
        return v


@lru_cache()
def get_config() -> Configuration:
    return Configuration()
