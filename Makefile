export PYTHONPATH=$(PWD):$(PWD)/src

all:

clean:
	rm -rf sources-orig.csv feed.json sources.json sources.json report.json feed/
	rm -rf __pycache__ */__pycache__ .pytest_cache

pytest:
	echo Running pytest...
	pytest -s tests/

validjson:
	export PYTHONPATH=$PWD:$PWD/src
	mv sources/sources.csv sources/sources-orig.csv ; head -10 sources/sources-orig.csv > sources/sources.csv
	echo Checking that csv_to_json.py creates valid JSON files...
	NO_UPLOAD=1 NO_DOWNLOAD=1 python src/csv_to_json.py
	mv sources/sources-orig.csv sources/sources.csv
	json_verify < output/sources.json
	json_verify < output/feed.json
	echo Checking that sources.json is of the expected size...
	test `stat -c%s output/sources.json` -gt 10
	echo Checking that feed.json is of the expected size...
	test `stat -c%s output/feed.json` -gt 10
	echo Checking that feed_processor_multi.py creates a valid JSON file...
	NO_UPLOAD=1 NO_DOWNLOAD=1 python src/feed_processor_multi.py feed
	json_verify < output/feed/feed.json
	echo Checking that the report makes sense...
	python lib/report-check.py
	echo Checking that feed/feed.json is of the expected size...
	test `stat -c%s output/feed/feed.json` -gt 1000

test: pytest validjson
