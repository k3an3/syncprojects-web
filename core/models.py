import base64

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser, User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


# noinspection PyUnusedLocal
@receiver(post_save, sender=get_user_model())
def create_core_user(sender, instance, created, **kwargs):
    if created:
        CoreUser.objects.create(user=instance)


class Project(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(default=timezone.now)
    image = models.ImageField(null=True, blank=True)
    sync_enabled = models.BooleanField(default=True)
    seafile_uuid = models.UUIDField(null=True, blank=True)

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
        return self.user.username


class Song(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    url = models.CharField(max_length=300, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    sync_enabled = models.BooleanField(default=True)
    directory_name = models.CharField(max_length=200, null=True, blank=True)
    last_mtime = models.DateTimeField(null=True, blank=True)
    peaks = models.TextField(null=True, blank=True)

    # TODO: Songs themselves should have locks. Replicate or move functionality from projects
    def __str__(self):
        return self.name

    def encode_url(self):
        return 'ebsfm:' + base64.b64encode(self.url.encode()).decode()
