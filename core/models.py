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
    directory_name = models.CharField(max_length=200)
    sync_enabled = models.BooleanField(default=True)

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

    def member_of(self, project: Project):
        try:
            return self.projects.get(id=project.id)
        except Project.DoesNotExist:
            return False

    def __str__(self):
        return self.user.username


class Song(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    url = models.CharField(max_length=300, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    sync_enabled = models.BooleanField(default=True)

    def __str__(self):
        return self.name
