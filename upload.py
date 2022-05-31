import logging

import boto3
from botocore.exceptions import ClientError

import config

boto_session = boto3.Session()
s3_client = boto_session.client('s3')


class InvalidS3Bucket(Exception):
    pass


def upload_file(file_name, bucket, object_name=None):
    if object_name is None:
        object_name = file_name
    try:
        if bucket == config.PUB_S3_BUCKET:
            s3_client.upload_file(file_name, bucket, object_name, ExtraArgs={
                'GrantRead': f'id={config.BRAVE_TODAY_CLOUDFRONT_CANONICAL_ID}',
                'GrantFullControl': f'id={config.BRAVE_TODAY_CANONICAL_ID}'
            })
        elif bucket == config.PRIV_S3_BUCKET:
            s3_client.upload_file(file_name, bucket, object_name, ExtraArgs={
                'GrantRead': f'id={config.PRIVATE_CDN_CANONICAL_ID}',
                'GrantFullControl': f'id={config.PRIVATE_CDN_CLOUDFRONT_CANONICAL_ID}'
            })
        else:
            raise InvalidS3Bucket("Attempted to upload to unknown S3 bucket.")

    except ClientError as e:
        logging.error(e)
        return False
    return True
