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


class ClientConfig(models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)
    last_updated = models.DateTimeField(default=timezone.now)
    sync_root = models.TextField(help_text="Absolute path to the root directory where your song project files will be "
                                           "synced.")
    flat_layout = models.BooleanField(default=False, help_text="Whether to keep all song project files in one folder, "
                                                               "or separate them by project.")


class ClientUpdate(models.Model):
    version = models.CharField(max_length=20, unique=True)
    updater = models.FileField(upload_to='updates/updater/', null=True, blank=True)
    package = models.FileField(upload_to='updates/')

    def __str__(self):
        return f"Update v{self.version}"

    def latest_updater(self) -> str:
        if self.updater:
            return self.updater.url
        try:
            return ClientUpdate.objects.filter(~Q(updater='')).order_by('-id')[0].updater.url
        except IndexError:
            return None


class ChangelogEntry(models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    entry = models.TextField()
    date_created = models.DateTimeField(default=timezone.now)
