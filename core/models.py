import base64

from django.contrib.auth.models import AbstractUser, User
from django.db import models
from django.urls import reverse
from django.utils import timezone



class Project(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(default=timezone.now)
    image = models.ImageField(null=True, blank=True)
    sync_enabled = models.BooleanField(default=True)
    seafile_uuid = models.UUIDField(null=True, blank=True, help_text="ID of project from Seafile (optional)")

    def __str__(self):
        return self.name

    def songs(self):
        return self.song_set.all()

    def locks(self):
        return self.lock_set.all()

    def is_locked(self) -> bool:
        for lock in self.locks():
            if not lock.end_time or lock.end_time > timezone.now():
                return lock
            lock.delete()
        return False

    def is_locked_by_user(self, user):
        # TODO: has anyone else locked it?
        # TODO: maybe query directly
        if lock := self.is_locked():
            f = lock.user == user
            return f
        return False

    def syncs(self, count: int = 10):
        return self.sync_set.all()[:count]

    def unlock(self):
        for lock in self.locks():
            lock.delete()

    def get_absolute_url(self):
        return reverse('core:project-detail', kwargs={'pk': self.pk})


class CoreUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    projects = models.ManyToManyField(Project)

    def has_access_to(self, obj):
        if isinstance(obj, Project):
            try:
                return self.projects.get(id=obj.id)
            except Project.DoesNotExist:
                return False
        elif isinstance(obj, Song):
            try:
                return self.projects.get(id=obj.project.id)
            except Project.DoesNotExist:
                return False
        else:
            raise NotImplementedError()

    def __str__(self):
        return self.user.first_name or self.user.username


class Song(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    url = models.CharField(max_length=300, null=True, blank=True,
                           help_text="URL to audio file for this song (optional)")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    sync_enabled = models.BooleanField(default=True)
    directory_name = models.CharField(max_length=200, null=True, blank=True,
                                      help_text="Specify a different folder name for Syncprojects-client to use (optional)")
    last_mtime = models.DateTimeField(null=True, blank=True)
    peaks = models.TextField(null=True, blank=True)

    # TODO: Songs themselves should have locks. Replicate or move functionality from projects
    def __str__(self):
        return self.name

    def encode_url(self):
        return 'ebsfm:' + base64.b64encode(self.url.encode()).decode()

    def clear_peaks(self):
        self.peaks = ''
        self.save()

    def get_absolute_url(self):
        return reverse('core:song-detail', kwargs={'proj': self.project.id, 'song': self.id})
