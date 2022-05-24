import json
import logging
import sys


def check_report(report):
    success = True
    for feed in report['feed_stats']:
        get_size = report['feed_stats'][feed]['size_after_get']
        insert_size = report['feed_stats'][feed]['size_after_insert']
        if insert_size > get_size:
            logging.error(
                "Logic error: we inserted %s posts but only downloaded %s.", insert_size, get_size)
            success = False

        if get_size == 0:
            logging.error("Didn't get any posts from %s.", feed)
            success = False

        if insert_size == 0:
            logging.error("Didn't insert any posts from %s.", feed)
            success = False

    return success


with open("report.json", encoding="utf-8") as f:
    if not check_report(json.loads(f.read())):
        sys.exit(1)
