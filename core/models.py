import base64
import re
from datetime import timedelta

import timeago
from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.urls import reverse
from django.utils import timezone

from core.s3 import get_client, get_presigned_url, PRESIGNED_URL_DURATION, get_song_names, FAILURE_RETRY_INTERVAL
from syncprojectsweb.settings import AUTH_USER_MODEL


class Lock(models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True, blank=True)
    reason = models.CharField(max_length=100, null=True, blank=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return f"{self.object} locked by {self.user} because {self.reason}"


class LockableModel:
    def is_locked(self) -> bool:
        for lock in self.locks.all():
            if not lock.end_time or lock.end_time > timezone.now():
                return lock
            lock.delete()
        return False

    def is_locked_by_user(self, user):
        # TODO: has anyone else locked it?
        # TODO: maybe query directly
        if lock := self.is_locked():
            return lock.user == user
        return False

    def unlock(self):
        for lock in self.locks.all():
            lock.delete()


class Project(models.Model, LockableModel):
    PUBLIC = 'public'
    UNLISTED = 'unlisted'
    INVITE = 'invite'
    SHARING_CHOICES = (
        (PUBLIC, 'Public'),
        (UNLISTED, 'Unlisted'),
        (INVITE, 'Invite Only')
    )
    name = models.CharField(max_length=100)
    bio = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    image = models.ImageField(null=True, blank=True)
    sync_enabled = models.BooleanField(default=True)
    sharing = models.CharField(max_length=10, default=INVITE, choices=SHARING_CHOICES)
    locks = GenericRelation(Lock)

    def __str__(self):
        return self.name

    def songs(self):
        return self.song_set.all()

    def syncs(self, count: int = 10):
        return self.sync_set.all()[:count]

    def get_absolute_url(self):
        return reverse('core:project-detail', kwargs={'pk': self.pk})


class Album(models.Model):
    name = models.CharField(max_length=100)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    cover = models.ImageField(null=True, blank=True)
    released = models.BooleanField(default=False)
    release_date = models.DateField(null=True, blank=True,
                                    help_text="If the album is not released yet, this can be used to specify the "
                                              "estimated release date. YYYY-MM-DD")

    def __str__(self) -> str:
        return self.name


class Song(models.Model, LockableModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    url = models.CharField(max_length=300, null=True, blank=True,
                           help_text="URL to audio file for this song (optional)")
    url_last_fetched = models.DateTimeField(null=True, blank=True)
    url_last_error = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    sync_enabled = models.BooleanField(default=True)
    directory_name = models.CharField(max_length=200, null=True, blank=True,
                                      help_text="Specify a different folder name for Syncprojects-client to use ("
                                                "optional)")
    project_file = models.CharField(max_length=200, null=True, blank=True, help_text="By default, the most recently "
                                                                                     "edited .cpr file is opened. Use"
                                                                                     " this to supply a custom filename.")
    last_mtime = models.DateTimeField(null=True, blank=True)
    peaks = models.TextField(null=True, blank=True)
    locks = GenericRelation(Lock)
    shared_with_followers = models.BooleanField(default=False)
    album = models.ForeignKey(Album, null=True, blank=True, on_delete=models.SET_NULL)
    album_order = models.PositiveIntegerField(null=True, blank=True)
    bpm = models.PositiveIntegerField(null=True, blank=True)
    archived = models.BooleanField(default=False, help_text="Prevent further syncs to this song. It can be "
                                                            "downloaded, but no new changes made.")
    key_tuning = models.CharField(max_length=40, verbose_name="Key/tuning", null=True, blank=True,
                                  help_text="E.g. G# Minor, Half-step down tuning")

    def __str__(self):
        return self.name

    def encode_url(self):
        return 'ebsfm:' + base64.b64encode(self.url.encode()).decode()

    def clear_peaks(self):
        self.peaks = ''
        self.save()

    def get_absolute_url(self):
        return reverse('core:song-detail', kwargs={'proj': self.project.id, 'song': self.id})

    @property
    def revision(self) -> int:
        return len(self.sync_set.all())

    def should_fetch_url(self) -> bool:
        now = timezone.now()
        if not self.url_last_fetched:
            if not self.url_last_error or now >= self.url_last_error + timedelta(seconds=FAILURE_RETRY_INTERVAL):
                return True
        elif now >= self.url_last_fetched + timedelta(seconds=PRESIGNED_URL_DURATION):
            return True
        return False

    @property
    def signed_url(self):
        if self.should_fetch_url():
            if self.name.lower() in (names := get_song_names(get_client(), self.project)):
                self.url = get_presigned_url(get_client(), names[self.name.lower()])
                self.url_last_fetched = timezone.now()
            else:
                self.url_last_error = timezone.now()
            self.save()
        return self.url


class FeatureChangelog(models.Model):
    date = models.DateField(default=timezone.now)
    changes = models.TextField()

    def __str__(self):
        return str(self.date)

    def format_changes(self):
        return re.sub(r'((^|\n)##?) ', r'\1##', self.changes)


class Comment(models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)
    assignee = models.ForeignKey(AUTH_USER_MODEL, related_name='assignee', null=True, blank=True,
                                 on_delete=models.SET_NULL)
    requires_resolution = models.BooleanField(default=False)
    resolved = models.BooleanField(default=False)
    posted_date = models.DateTimeField(default=timezone.now)
    edited = models.BooleanField(default=False)
    song_time = models.DurationField(null=True, blank=True)
    text = models.TextField()
    song = models.ForeignKey(Song, null=True, blank=True, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, null=True, blank=True, on_delete=models.CASCADE)
    likes = models.PositiveIntegerField(default=0)

    def when_str(self):
        return timeago.format(self.posted_date, timezone.now())

    def timecode(self):
        seconds = int(self.song_time.total_seconds())
        minutes = seconds // 60
        hours = minutes // 60
        seconds = seconds % 60
        result = ""
        if hours:
            result += f"{hours}:"
        return result + f"{minutes}:{seconds:02}"

    def __str__(self):
        return self.user.username + " at " + self.posted_date.isoformat() + " says \"" + self.text[:50] + (
            "..." if len(self.text) > 50 else "") + "\""
