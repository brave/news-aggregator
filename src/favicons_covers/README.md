# Cover Images pipeline

The `cover_images.py` pipeline downloads and processes cover images from website URLs.
It fetches the cover image URLs from the specified websites, process the images using `wasm` binary and cache it to S3.

## Usage

```
export PYTHONPATH=$PWD:$PWD/src
NO_UPLOAD=1 NO_DOWNLOAD=1 python cover_images.py
```

## Workflow
### `process_site` function
The `process_site` function is designed to retrieve information about a given domain, specifically focusing on
obtaining the site's cover image and background color. The function makes use of various methods to fetch this
information, employing multiple fallback mechanisms to ensure robustness in case of failures.

1. **Fetching Favicon using Google's Service:**
    - First attempt to fetch the cover image using Google's Favicon API.
    - If successful, retrieve the cover image and check its size. If the size is too small, raise a `ValueError`.
    - Obtain the background color associated with the cover image.
2. **Fallback to Alternative cover image Retrieval:**
    - If the previous step fails, try an alternative method to obtain the cover image by calling `get_best_image(domain)`.
    - If successful, retrieve the cover image and its URL.
    - Obtain the background color associated with the cover image.
3. **Fallback to Clearbit Service:**
   - If the previous steps fail, attempt to fetch the cover image using Clearbit's API.
   - If successful, retrieve the cover image and check its size. If the size is too small, raise a `ValueError`.
   - Obtain the background color associated with the cover image.
4. **Fallback to Metadata Parsing:**
   - If all previous attempts fail, try parsing the metadata of the page using `metadata_parser`.
   - Extract the image URL from the metadata and retrieve the cover image.
   - Obtain the background color associated with the cover image.
5. **Error Handling:**
   - Handle various exceptions that may occur during the process, logging errors and setting `image_url` to `None`
in case of failure.


#### Output
The function returns a tuple containing the domain, cover image URL, and background color.
The elements of the tuple are as follows:

- domain (str): The input domain.
- image_url (str): The URL of the retrieved cover image.
- background_color (str): The background color associated with the cover image.


### `get_background_color` function
The `get_background_color` function is responsible for determining the background color of an icon image. Here is the workflow:

1. If the image is monochromatic, it returns the hex color `#FFFFFF` (white).
2. It iterates over the edge pixels of the image, both vertically and horizontally, and collects their colors.
3. It discards any transparent colors and sorts the collected colors based on their length.
4. It selects the middle color from the sorted colors list as the background color of the image.

#### Output
The function returns the determined background color as a hexadecimal string. If the image is monochromatic,
it defaults to white (#FFFFFF). If the image has no discernible colors, it returns None.


### `process_cover_image` function
The `process_cover_image` function is responsible for processing the cover images, pad and cache them to the S3.

### Code Quality
The function contains a `noqa: C901` comment, indicating that it ignores a warning related to a large function.
Consider refactoring the function into smaller, more modular components for better maintainability and testability.
