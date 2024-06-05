# Copyright (c) 2023 The Brave Authors. All rights reserved.
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at https://mozilla.org/MPL/2.0/. */

from datetime import datetime
from typing import Any, Optional

import bleach
from pydantic import HttpUrl, model_validator

from models.base import Model


class FeedBase(Model):
    category: str
    publish_time: datetime
    url: str
    img: Optional[HttpUrl] = None
    title: str
    description: Optional[str] = None
    content_type: str
    publisher_id: str
    publisher_name: str
    creative_instance_id: str = ""
    url_hash: str
    padded_img: Optional[HttpUrl] = None
    score: float

    @model_validator(mode="before")
    @classmethod
    def bleach_each_value(cls, values: dict) -> dict[str, Any]:
        for k, v in values.items():
            if isinstance(v, str):
                values[k] = bleach.clean(v, strip=True).replace(
                    "&amp;", "&"
                )  # workaround limitation in bleach

        return values
