# Copyright (c) 2023 The Brave Authors. All rights reserved.
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at https://mozilla.org/MPL/2.0/. */

import math
from typing import Tuple

import structlog

logger = structlog.getLogger(__name__)


def fade_to_brighter_color(hex_color, fade_factor=0.12):
    # Convert hex color string to an RGB tuple
    hex_color = tuple(int(hex_color[i : i + 2], 16) for i in (1, 3, 5))

    # Calculate the blended RGB color
    faded_color = tuple(int(c + fade_factor * (255 - c)) for c in hex_color)

    # Ensure that the resulting color components do not exceed 255
    faded_color = tuple(min(255, max(0, c)) for c in faded_color)

    # Convert the blended RGB color back to a hex color
    faded_hex_color = "#{:02X}{:02X}{:02X}".format(*faded_color)

    return faded_hex_color


# def is_monochromatic(image, tolerance=60):
#     try:
#         grayscale_image = image.convert("LA")
#         grayscale_array = np.array(grayscale_image)
#
#         scaled_grayscale_array = np.where(
#             grayscale_array > 200, grayscale_array * 1.5, grayscale_array
#         )
#         scaled_std_deviation = np.std(scaled_grayscale_array)
#
#         # Check if the image is monochromatic (low standard deviation)
#         return scaled_std_deviation < tolerance
#     except Exception as e:
#         logger.info(f"Error: {str(e)}")
#         return False


def is_monochromatic(img, variance_threshold=100):
    try:
        img = img.convert("RGBA")

        # Get the image data
        data = img.getdata()
        # Calculate the color variance
        variance = sum(
            (
                abs(pixel[0] - pixel[1])
                + abs(pixel[1] - pixel[2])
                + abs(pixel[2] - pixel[0])
            )
            / 3
            for pixel in data
        ) / len(data)

        return variance < variance_threshold
    except Exception as e:
        logger.info(f"Error: {e}")
        return False


def hex_color(col: Tuple[int, int, int]):
    """Converts a [r, g, b] tuple to it's hex representation. Transparency is ignored"""

    def h(c):
        return hex(int(c))[2:].zfill(2)

    return f"#{h(col[0])}{h(col[1])}{h(col[2])}"


def is_transparent(col: Tuple[int, int, int, int], threshold=1):
    return col[3] < 255 * threshold


def color_length(color: Tuple[int, int, int]):
    """Gets the length of the color. Ignores transparency"""
    return math.sqrt(color[0] ** 2 + color[1] ** 2 + color[2] ** 2)
