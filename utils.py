import glob
import logging
import mimetypes
import re
from typing import List
from urllib.parse import urlparse

import boto3
from botocore.exceptions import ClientError

import config

boto_session = boto3.Session()
s3_client = boto_session.client('s3')

domain_url_fixer = re.compile(r"^https://(www\.)?|^")
subst = "https://www."


class InvalidS3Bucket(Exception):
    pass


def upload_file(file_name, bucket, object_name=None):
    if object_name is None:
        object_name = file_name
    try:
        content_type = mimetypes.guess_type(file_name)[0] or 'binary/octet-stream'
        if bucket == config.PUB_S3_BUCKET:
            s3_client.upload_file(file_name, bucket, object_name, ExtraArgs={
                'GrantRead': 'id=%s' % config.BRAVE_TODAY_CLOUDFRONT_CANONICAL_ID,
                'GrantFullControl': 'id=%s' % config.BRAVE_TODAY_CANONICAL_ID,
                'ContentType': content_type
            })
        elif bucket == config.PRIV_S3_BUCKET:
            s3_client.upload_file(file_name, bucket, object_name, ExtraArgs={
                'GrantRead': 'id=%s' % config.PRIVATE_CDN_CANONICAL_ID,
                'GrantFullControl': 'id=%s' % config.PRIVATE_CDN_CLOUDFRONT_CANONICAL_ID,
                'ContentType': content_type
            })
        else:
            raise InvalidS3Bucket("Attempted to upload to unknown S3 bucket.")

    except ClientError as e:
        logging.error(e)
        return False
    return True


def download_file(file_name, bucket, object_name=None):
    if object_name is None:
        object_name = file_name

    try:
        if bucket == config.PUB_S3_BUCKET:
            s3_client.download_file(bucket, object_name, file_name)
        elif bucket == config.PRIV_S3_BUCKET:
            s3_client.download_file(bucket, object_name, file_name)
        else:
            raise InvalidS3Bucket("Attempted to upload to unknown S3 bucket.")

    except ClientError as e:
        logging.error(e)
        return False
    return True


def ensure_scheme(domain):
    """Helper utility for ensuring a domain has a scheme. If none is attached
       this will use the https scheme.

       Note: this will break if domain has a non http(s) scheme.
       example.com ==> https://www.example.com
       https://example.com ==> https://www.example.com
       file://example.com ==> https://file://example.com
    """
    return domain_url_fixer.sub(subst, domain, 1)


def get_all_domains() -> List[str]:
    """Helper utility for getting all domains across all sources"""
    source_files = glob.glob('sources*.csv')
    result = set()
    for source_file in source_files:
        with open(source_file) as f:
            # Skip the first line, with the headers.
            lines = f.readlines()[1:]

            # The domain is the first field on the line
            yield from [line.split(',')[0].strip() for line in lines]


def uri_validator(x):
    """
    'http://www.cwi.nl:80/%7Eguido/Python.html' False
    '/data/Python.html' False
    '532' False
    u'dkakasdkjdjakdjadjfalskdjfalk' False
    'https://stackoverflow.com' True

    :param x: URL
    :return: bool
    """
    try:
        result = urlparse(x)
        return all([result.scheme, result.scheme == "https", result.netloc])
    except Exception as e:
        return False
