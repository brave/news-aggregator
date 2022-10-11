import os

USER_AGENT = 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Mobile Safari/537.36'

# Canonical ID of the public S3 bucket
BRAVE_TODAY_CANONICAL_ID = os.getenv('BRAVE_TODAY_CANONICAL_ID', None)
BRAVE_TODAY_CLOUDFRONT_CANONICAL_ID = os.getenv('BRAVE_TODAY_CLOUDFRONT_CANONICAL_ID', None)

# Set the number of processes to spawn for all multiprocessing tasks.
CONCURRENCY = max(1, int(os.getenv('CONCURRENCY', os.cpu_count())))

# Set to INFO to see some output during long-running steps.
LOG_LEVEL = os.getenv('LOG_LEVEL', 'WARNING')

# Disable uploads and downloads to S3. Useful when running locally or in CI.
NO_UPLOAD = os.getenv('NO_UPLOAD', None)
NO_DOWNLOAD = os.getenv('NO_DOWNLOAD', None)

PCDN_URL_BASE = os.getenv('PCDN_URL_BASE', 'https://pcdn.brave.software')
# Canonical ID of the private S3 bucket
PRIVATE_CDN_CANONICAL_ID = os.getenv('PRIVATE_CDN_CANONICAL_ID', None)
PRIVATE_CDN_CLOUDFRONT_CANONICAL_ID = os.getenv('PRIVATE_CDN_CLOUDFRONT_CANONICAL_ID', None)
PRIV_S3_BUCKET = os.getenv('PRIV_S3_BUCKET', 'brave-private-cdn-development')
PUB_S3_BUCKET = os.getenv('PUB_S3_BUCKET', 'brave-today-cdn-development')
SENTRY_URL = os.getenv('SENTRY_URL', '')
SOURCES_FILE = os.getenv('SOURCES_FILE', 'sources')
GLOBAL_SOURCES_FILE = os.getenv('GLOBAL_SOURCES_FILE', 'sources.global')
FAVICON_LOOKUP_FILE = os.getenv('FAVICON_LOOKUP_FILE', 'favicon_lookup')
COVER_INFO_LOOKUP_FILE = os.getenv('COVER_INFO_LOOKUP_FILE', 'cover_info_lookup')

MARK_SIMILARITY = os.getenv('MARK_SIMILARITY', False)
MARK_SIMILARITY_THRESHOLD = os.getenv('MARK_SIMILARITY_THRESHOLD', 0.65)
