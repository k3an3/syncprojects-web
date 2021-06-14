import io
from zipfile import ZipFile

import timeago
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Q
from django.utils import timezone

from core.models import Project, Song
from syncprojectsweb.settings import AUTH_USER_MODEL


class Sync(models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    sync_time = models.DateTimeField(default=timezone.now)
    songs = models.ManyToManyField(Song)

    def last_sync_str(self):
        return timeago.format(self.sync_time, timezone.now())

    def __str__(self):
        return f"{self.user} sync at {self.sync_time}"


class SupportedClientTarget(models.Model):
    target = models.CharField(max_length=100, unique=True)
    icon = models.CharField(max_length=50, null=True, blank=True)
    friendly_name = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.target

    def name(self) -> str:
        return self.friendly_name or self.target

    def render_icon(self) -> str:
        return f'<span class="fab fa-{self.icon}"></span>' if self.icon else ''

    def latest_release(self):
        return self.clientupdate_set.last()


class ClientUpdate(models.Model):
    version = models.CharField(max_length=20)
    updater = models.FileField(upload_to='updates/updater/', null=True, blank=True)
    package = models.FileField(upload_to='updates/')
    target = models.ForeignKey(SupportedClientTarget, null=True, blank=True, on_delete=models.PROTECT)

    def __str__(self):
        return f"v{self.version}-{self.target}"

    def latest_updater(self) -> str:
        if self.updater:
            return self.updater.url
        try:
            return ClientUpdate.objects.filter(~Q(updater=''), target=self.target).order_by('-id')[0].updater.url
        except IndexError:
            return None


class ChangelogEntry(models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    text = models.TextField()
    date_created = models.DateTimeField(default=timezone.now)
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    sync = models.ForeignKey(Sync, null=True, on_delete=models.SET_NULL, related_name='changelog')

    def __str__(self):
        return f"{self.date_created.isoformat()} by {self.user} on {self.song}"


class ClientLog(models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)
    log_compressed = models.BinaryField()

    def __str__(self):
        return f"{self.user} - {self.date}"

    def uncompressed(self):
        z = io.BytesIO(self.log_compressed)
        with ZipFile(z) as z:
            with z.open(z.namelist()[0]) as log:
                return log.read().decode()
