import timeago
from django.contrib.auth.models import AbstractUser, User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


# noinspection PyUnusedLocal
@receiver(post_save, sender=User)
def create_core_user(sender, instance, **kwargs):
    CoreUser.objects.get_or_create(user=instance)


class Project(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(default=timezone.now)
    image = models.ImageField(null=True, blank=True)

    def __str__(self):
        return self.name

    def songs(self):
        return self.song_set.all()

    def locks(self):
        return self.lock_set.all()

    def is_locked(self) -> bool:
        for lock in self.locks():
            if not lock.end_time or lock.end_time > timezone.now():
                return True
            lock.delete()
        return False

    def is_locked_by_user(self, user):
        return self.is_locked() and len(self.lock_set.filter(user=user)) > 0


class CoreUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    projects = models.ManyToManyField(Project)

    def member_of(self, project: Project):
        try:
            return self.projects.get(id=project.id)
        except Project.DoesNotExist:
            return False


class Song(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    url = models.CharField(max_length=300, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    sync_enabled = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Lock(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True, blank=True)
    reason = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.project} locked by {self.name} because {self.reason}"


# TODO: move to syncprojects app
class Sync(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    sync_time = models.DateTimeField(default=timezone.now)

    def last_sync_str(self):
        return timeago.format(self.sync_time, timezone.now())

    def __str__(self):
        return f"{self.user} sync at {self.sync_time}"
