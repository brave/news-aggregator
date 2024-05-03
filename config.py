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
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

logger = structlog.getLogger(__name__)


class Configuration(BaseSettings):
    default_headers = {
        "Accept": "*/*",
    }

    tz = timezone("UTC")
    request_timeout = 30
    max_content_size = 10000000

    output_feed_path: Path = Field(default=Path(__file__).parent / "output/feed")
    output_path: Path = Field(default=Path(__file__).parent / "output")
    wasm_thumbnail_path: Path = Field(
        default=Path(__file__).parent / "wasm_thumbnail.wasm"
    )
    img_cache_path: Path = Field(default=Path(__file__).parent / "output/feed/cache")
    feed_path = "feed"
    feed_sources_path = "feed_source.json"

    # Set the number of processes to spawn for all multiprocessing tasks.
    concurrency: int = cpu_count() - 1
    thread_pool_size: int = cpu_count() * 5

    # Disable uploads and downloads to S3. Useful when running locally or in CI.
    no_upload: Optional[str] = None
    no_download: Optional[str] = None
    min_image_size = 400

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
    tests_data_dir: Path = Field(default=Path(__file__).parent / "tests/tests_data")

    sentry_dsn: str = ""

    log_level: str = "info"

    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.getLevelName(log_level.upper())
        ),
    )

    if sentry_dsn:
        import sentry_sdk

        sentry_sdk.init(dsn=sentry_dsn, traces_sample_rate=0)

    prom_pushgateway_url: Optional[str] = None

    prometheus_multiproc_dir: Path = Field(
        default=Path(__file__).parent / "output/prom_tmp"
    )

    bs_pop_endpoint: str = ""
    pop_score_cutoff = 300
    pop_score_exponent = 2 / 3
    pop_score_range = 100

    nu_api_url: str = ""
    nu_api_token: str = ""
    nu_default_channels = ["Fun"]
    nu_augment_channels = [
        "Top Sources",
        "Top News",
        "World News",
        "US News",
        "Culture",
    ]
    nu_confidence_threshold = 0.9
    nu_excluded_channels = ["Crime"]

    video_extensions = (
        ".mp4",
        ".avi",
        ".mov",
        ".wmv",
        ".flv",
        ".mkv",
        ".webm",
        ".mpg",
        ".mpeg",
        ".3gp",
        ".ogg",
        ".ogv",
        ".rm",
        ".swf",
        ".vob",
    )

    database_url: Optional[str] = None
    schema_name: Optional[str] = "news"

    def get_db_session(self) -> Session:
        """
        Get a database session
        """
        engine = create_engine(self.database_url)
        return sessionmaker(bind=engine)()

    @validator("img_cache_path")
    def create_img_cache_path(cls, v: Path) -> Path:
        v.mkdir(parents=True, exist_ok=True)
        return v

    @validator("database_url")
    def get_database_url(cls, v) -> str:
        if v and v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql://")
        return v

    @validator("prometheus_multiproc_dir")
    def create_prometheus_multiproc_dir(cls, v: Path) -> Path:
        v.mkdir(parents=True, exist_ok=True)
        os.environ["PROMETHEUS_MULTIPROC_DIR"] = str(v)
        return v


@lru_cache()
def get_config() -> Configuration:
    return Configuration()
