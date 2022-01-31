from os.path import basename

import boto3
from typing import Set, List

from syncprojectsweb.settings import BACKEND_ACCESS_ID, BACKEND_SECRET_KEY, BACKEND_BUCKET

PRESIGNED_URL_DURATION = 3600 * 24 * 30
FAILURE_RETRY_INTERVAL = 60 * 15


class S3Client:
    _session = None

    def __new__(cls, *args, **kwargs):
        if not cls._session:
            cls._session = boto3.Session(
                aws_access_key_id=BACKEND_ACCESS_ID,
                aws_secret_access_key=BACKEND_SECRET_KEY
            )
        return super().__new__(cls)

    @property
    def client(self):
        return self._session.client('s3')

    @property
    def resource(self):
        return self._session.resource('s3')


def get_presigned_url(client, key: str, duration: int = PRESIGNED_URL_DURATION, method: str = 'get',
                      content_type: str = "", **kwargs) -> str:
    extra = {}
    if content_type:
        extra['ContentType'] = content_type
    if method == "get":
        return client.generate_presigned_url(
            ClientMethod=f'get_object',
            Params={
                'Bucket': BACKEND_BUCKET,
                'Key': key,
                **kwargs
            }, ExpiresIn=duration
        )
    elif method == "put":
        return client.generate_presigned_url(
            ClientMethod='put_object',
            Params={'Bucket': BACKEND_BUCKET, 'Key': key, **extra},
            ExpiresIn=3600)
    elif method == "upload":
        return client.generate_presigned_post(BACKEND_BUCKET, key)
    else:
        raise NotImplementedError()


def get_remote_files(client, prefix: str):
    if BACKEND_BUCKET:
        results = client.list_objects_v2(Bucket=BACKEND_BUCKET, Prefix=prefix)
        try:
            return results['Contents']
        except KeyError:
            pass
    return []


def get_song_names(client, project: str) -> Set:
    files = get_remote_files(client, f"{project}/")
    return {'.'.join(basename(f['Key']).split('.')[:-1]).lower(): f['Key'] for f in files}


def get_versions(s3, project: str, song: str) -> List:
    path = '/'.join((project, song))
    versions = []
    for version in s3.resource.Bucket(BACKEND_BUCKET).object_versions.filter(Prefix=path):
        versions.append((version, get_presigned_url(s3.client, version.key, VersionId=version.version_id)))
    return sorted(versions, key=lambda x: x[0].last_modified)
