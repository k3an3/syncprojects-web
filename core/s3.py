from os.path import basename
from typing import Set

import boto3

from syncprojectsweb.settings import BACKEND_ACCESS_ID, BACKEND_SECRET_KEY, BACKEND_BUCKET

PRESIGNED_URL_DURATION = 3600 * 24 * 30
FAILURE_RETRY_INTERVAL = 60 * 15


def get_client():
    return boto3.client(
        's3',
        aws_access_key_id=BACKEND_ACCESS_ID,
        aws_secret_access_key=BACKEND_SECRET_KEY
    )


def get_presigned_url(client, key: str, duration: int = PRESIGNED_URL_DURATION) -> str:
    return client.generate_presigned_url(
        ClientMethod='get_object',
        Params={
            'Bucket': BACKEND_BUCKET,
            'Key': key,
        }, ExpiresIn=duration
    )


def get_remote_files(client, prefix: str):
    results = client.list_objects_v2(Bucket=BACKEND_BUCKET, Prefix=prefix)
    try:
        return results['Contents']
    except KeyError:
        return []


def get_song_names(client, project: str) -> Set:
    files = get_remote_files(client, f"{project}/")
    return {'.'.join(basename(f['Key']).split('.')[:-1]).lower(): f['Key'] for f in files}
