from django.db import models
from django.utils import timezone

from core.models import Project
from core.s3 import get_presigned_url, get_client
from syncprojectsweb.settings import AUTH_USER_MODEL


class Snippet(models.Model):
    url = models.URLField(null=True, blank=True)
    name = models.CharField(max_length=50)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)

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

    def __str__(self):
        return self.name
