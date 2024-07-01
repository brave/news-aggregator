#!/bin/bash
# Copyright (c) 2023 The Brave Authors. All rights reserved.
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at https://mozilla.org/MPL/2.0/. */

set -euo pipefail
IFS=$'\n\t'

task="${1-run-all}"

mkdir -p output

function die_usage() {
  echo "$0 usage:"
  echo "  defaults to 'csv-to-json' command"
  echo ""
  echo "  $0 run-all                     Run all the required end-to-end (For deployment)"
  echo "  $0 favicons_covers             Run favicons and cover_images"
  echo "  $0 healthcheck                 Run healthcheck for status.brave.com"
  echo "  $0 shell                       Start a bpython shell"
  exit 1
}

if [[ "$task" = "run-all" ]]; then
  if [[ ! -d "output/" ]]; then
    echo "Error: output/ dir not found!"
    echo "Are you in the from root directory?"
    exit 1
  fi

  set -x

  echo "Init feed sources"
  python -u src/csv_to_json.py feed.json

  if [[ "$SOURCES_FILE" = "sources.en_US" ]]; then
    echo "Generating sources.global.json"
    python -u src/csv_to_global_json.py
  fi

  echo "Apply DB migrations"
  alembic upgrade head
  echo "Inserting publisher in DB"
  python -u src/db_crud.py

  echo "Starting main script..."
  mkdir -p output/feed/cache
  python -u src/main.py

elif [[ "$task" = "favicon-covers" ]]; then
  if [[ ! -d "output/" ]]; then
    echo "Error: output/ dir not found!"
    echo "Are you in the from root directory?"
    exit 1
  fi

  set -x

  echo "Fetching Favicons..."
  python -u src/favicons_covers/update_favicon_urls.py

  echo "Fetching Cover images"
  mkdir -p .cache
  python -u src/favicons_covers/cover_images.py

elif [[ "$task" = "healthcheck" ]]; then
  set -x
  echo "Starting health check job..."
  python -u src/healthcheck.py

elif [[ "$task" = "shell" ]]; then
  set -x
  bpython

elif [[ "$task" = "help" || "$task" = "-h" || "$task" = "--help" ]]; then
  die_usage

elif [ "$task" = "purgeall" ]; then
    echo "Down Migration"
    alembic downgrade base

else
  echo "unknown cmd: $task"
  die_usage
fi
