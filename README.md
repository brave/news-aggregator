# News Aggregator
This project is the backend side of Brave News, and it fetches the articles from the Brave-defined publishers and
shows their feeds/News in the Browser.

For more details: https://brave.com/brave-news-updates/

## Setup

### Dependencies
Python Version (Required):

    Python 3.9

Required setup:

    virtualenv -p /usr/bin/python3.9 .venv
    . .venv/bin/activate
    pip install -r requirements.dev.txt


### Running locally

To generate sources and list of feeds:

    export PYTHONPATH=$PWD:$PWD/src
    NO_UPLOAD=1 NO_DOWNLOAD=1 python src/csv_to_json.py

To generate browser feed and images:

    export PYTHONPATH=$PWD:$PWD/src
    NO_UPLOAD=1 python src/feed_processor_multi.py feed

To update the favicon urls:

    export PYTHONPATH=$PWD:$PWD/src
    NO_UPLOAD=1 NO_DOWNLOAD=1 python src/favicons_covers/update_favicon_urls.py

### Organization

This service organizes as follows:
```
news_aggregator/
├── bin/                # This dir contains the helping shell scripts for Dockerfile.
├── lib/                # This dir contains the utility modules.
├── models/             # This dir contains the dataclasses.
├── sources/            # This dir contains the sources files.
├── src/                # This dir contains all the python script to run the new aggregator.
├── tests/              # This dir contains the tests.
```

### Contribution

We configured the pre-commit hooks to ensure the quality of the code. To set-up the pre-commit hooks run the following
commands:

    pre-commit install
    pre-commit run --all-files


# wasm_thumbnail

The `wasm_thumbnail.wasm` binary comes from <https://github.com/brave-intl/wasm-thumbnail>.
