from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from core.s3 import get_presigned_url, get_client


class Snippet(models.Model):
    url = models.URLField(null=True, blank=True)
    name = models.CharField(max_length=50)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    object = GenericForeignKey('content_type', 'object_id')

    # TODO: security

    def get_upload_url(self):
        if not self.url:
            import secrets
            suffix = secrets.token_urlsafe(6)
            *name, extension = self.name.split('.')
            key = f"{'.'.join(name)}-{object.name}-{suffix}.{extension}"
            url = get_presigned_url(get_client(), key, method="upload")
            self.url, fields = url['url'], url['fields']
            return self.url, fields
