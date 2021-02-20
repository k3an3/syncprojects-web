import timeago
from django.contrib.auth.models import User
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


class Lock(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True, blank=True)
    reason = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.project} locked by {self.user} because {self.reason}"
