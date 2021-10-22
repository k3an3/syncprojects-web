from django.db import models
from django.utils import timezone

from core.models import Project, S3ExpiringModelMixin
from core.s3 import get_presigned_url, get_client
from syncprojectsweb.settings import AUTH_USER_MODEL


class Snippet(S3ExpiringModelMixin):
    match_required = False
    display_name = models.CharField(max_length=50, null=True, blank=True)
    name = models.CharField(max_length=50)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)

    def upload_url(self):
        import secrets
        suffix = secrets.token_urlsafe(6)
        *name, extension = self.name.split('.')
        self.display_name = '.'.join(name)
        self.name = f"snippets/{self.project.name}-{'.'.join(name)}_{suffix}.{extension}"
        url = get_presigned_url(get_client(), self.name, method="put", content_type="audio/ogg; codecs=opus")
        self.save()
        return url

    def __str__(self):
        try:
            return self.display_name + ", " + self.project.name
        except TypeError:
            return self.name + ", " + self.project.name
