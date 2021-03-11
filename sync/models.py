import timeago
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone

from core.models import Project, Song


class Sync(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    sync_time = models.DateTimeField(default=timezone.now)
    songs = models.ManyToManyField(Song)

    def last_sync_str(self):
        return timeago.format(self.sync_time, timezone.now())

    def __str__(self):
        return f"{self.user} sync at {self.sync_time}"


class ClientUpdate(models.Model):
    version = models.CharField(max_length=20, unique=True)
    _updater = models.FileField(upload_to='updates/updater/', null=True, blank=True)
    package = models.FileField(upload_to='updates/')

    def __str__(self):
        return f"Update v{self.version}"

    def updater(self) -> str:
        if self._updater:
            return self._updater
        return ClientUpdate.objects.filter(_updater__isnull=False)[0]
