from django.db import models
from django.utils import timezone

from core.models import Project, S3ExpiringModelMixin
from core.s3 import get_presigned_url, S3Client
from syncprojectsweb.settings import AUTH_USER_MODEL

CONTENT_TYPES = {
    'ogg': 'audio/ogg; codecs=opus',
    'mp3': 'audio/mpeg',
    'm4a': 'audio/x-m4a'
}


class Snippet(S3ExpiringModelMixin):
    match_required = False
    display_name = models.CharField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=255)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)

    def upload_url(self):
        import secrets
        suffix = secrets.token_urlsafe(6)
        *name, extension = self.name.split('.')
        self.display_name = '.'.join(name)
        self.name = f"snippets/{self.project.name}-{'.'.join(name)}_{suffix}.{extension}"
        content_type = CONTENT_TYPES.get(extension, f'audio/{extension}')
        url = get_presigned_url(S3Client().client, self.name, method="put", content_type=content_type)
        self.save()
        return url

    def __str__(self):
        try:
            return self.display_name + ", " + self.project.name
        except TypeError:
            return self.name + ", " + self.project.name
