# Copyright (c) 2023 The Brave Authors. All rights reserved.
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at https://mozilla.org/MPL/2.0/. */

import hashlib
from typing import Any, Dict, List, Optional

import bleach
from pydantic import Field, field_validator, model_validator
from pydantic_core.core_schema import ValidationInfo

from models.base import Model


class PublisherBase(Model):
    enabled: bool = Field(alias="Status")
    publisher_name: str = Field(alias="Title")
    category: str = Field(alias="Category")
    site_url: str = Field(alias="Domain")
    feed_url: str = Field(alias="Feed")
    favicon_url: Optional[str] = Field(default=None)
    cover_url: Optional[str] = Field(default=None)
    background_color: Optional[str] = Field(default=None)
    score: float = Field(default=0, alias="Score")
    destination_domains: list[str] = Field(alias="Destination Domains")
    original_feed: Optional[str] = Field(default=None, alias="Original_Feed")
    og_images: bool = Field(default=None, alias="OG-Images")
    max_entries: int = Field(default=20)
    creative_instance_id: str = Field(default="", alias="Creative Instance ID")
    content_type: str = Field(default="article", alias="Content Type")
    publisher_id: str = Field(default="", alias="Publisher ID", validate_default=True)

    @model_validator(mode="before")
    def bleach_each_value(cls, values: dict) -> Dict[str, Any]:
        for k, v in values.items():
            if isinstance(v, str):
                values[k] = bleach.clean(v, strip=True).replace(
                    "&amp;", "&"
                )  # workaround limitation in bleach

        return values

    @field_validator("enabled", mode="before", check_fields=False)
    def fix_enabled_format(cls, v: str) -> bool:
        return v == "Enabled"

    @field_validator("score", mode="before", check_fields=False)
    def fix_score_format(cls, v: str) -> float:
        return v if v else 0

    @field_validator("og_images", mode="before", check_fields=False)
    def fix_og_images_format(cls, v: str) -> bool:
        return v == "On"

    @field_validator("publisher_name", mode="before", check_fields=False)
    def validate_publisher_name(cls, v: str) -> str:
        if not v:
            raise ValueError("must contain a value")
        return v

    @field_validator("destination_domains", mode="before", check_fields=False)
    def fix_destination_domains_format(cls, v: str) -> List[str]:
        if not v:
            raise ValueError("must contain a value")
        return v.split(";")

    @field_validator("publisher_id")
    def add_publisher_id(cls, v: str, info: ValidationInfo) -> str:
        original_feed = info.data.get("original_feed")
        feed_url = info.data.get("feed_url")

        feed_value = str(original_feed) if original_feed else str(feed_url)
        return hashlib.sha256(feed_value.encode("utf-8")).hexdigest()


class PublisherModel(PublisherBase):
    channels: Optional[list[str]] = Field(default=[], alias="Channels")
    rank: Optional[int] = Field(default=None, alias="Rank")

    @field_validator("rank", mode="before")
    def fix_rank_format(cls, v: str) -> Optional[int]:
        return int(v) if v else None

    @field_validator("channels", mode="before")
    def fix_channels_format(cls, v: str) -> Optional[List[str]]:
        return v.split(";") if v else []


class LocaleModel(Model):
    locale: str = ""
    channels: Optional[list[str]] = Field(default=[], alias="Channels")
    rank: Optional[int] = Field(default=None, alias="Rank")

    @field_validator("rank", mode="before", check_fields=False)
    def fix_rank_format(cls, v: str) -> Optional[int]:
        return int(v) if v else None

    @field_validator("channels", mode="before")
    def fix_channels_format(cls, v: str) -> Optional[List[str]]:
        return v.split(";") if v else []


class PublisherGlobal(PublisherBase):
    locales: list[LocaleModel] = []
