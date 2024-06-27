# Copyright (c) 2023 The Brave Authors. All rights reserved.
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at https://mozilla.org/MPL/2.0/. */

from orjson import orjson
from pydantic import BaseModel, ConfigDict


def orjson_dumps(v, *, default):
    # orjson.dumps returns bytes, to match standard json.dumps we need to decode
    return orjson.dumps(v, default=default).decode()


class Model(BaseModel):
    """
    To find all the configuration options for a model, just visit the link below
    https://pydantic-docs.helpmanual.io/usage/model_config/
    """

    model_config = ConfigDict(
        from_attributes=False,
        str_strip_whitespace=True,
        use_enum_values=False,
        validate_assignment=True,
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )
