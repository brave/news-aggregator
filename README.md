# News Aggregator

## Installation

Required setup:

    virtualenv -p /usr/bin/python3.9 .venv
    . .venv/bin/activate
    pip install -r requirements.txt

then if you want to run `make test`:

    pip install bandit pip-check-reqs pylint pytest safety
    apt install yajl-tools

## Running locally

To generate sources and list of feeds:

    NO_UPLOAD=1 python csv_to_json.py feed.json

To generate browser feed and images:

    NO_UPLOAD=1 python feed_processor_multi.py feed

To update the favicon urls:

    python update_favicon_urls.py
    NO_UPLOAD=1 python csv_to_json sources.json

# wasm_thumbnail

The `wasm_thumbnail.wasm` binary comes from <https://github.com/brave-intl/wasm-thumbnail>.
