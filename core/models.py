import base64
import re
from datetime import timedelta
from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone

from core.s3 import get_presigned_url, PRESIGNED_URL_DURATION, get_song_names, FAILURE_RETRY_INTERVAL, \
    S3Client
from syncprojectsweb.settings import AUTH_USER_MODEL


class Link(models.Model):
    url = models.URLField()
    name = models.CharField(max_length=100)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    object = GenericForeignKey('content_type', 'object_id')


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
    website = models.URLField(null=True, blank=True)
    links = GenericRelation(Link)

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
    links = GenericRelation(Link)

    def __str__(self) -> str:
        return self.name

    def is_released(self) -> bool:
        return self.released and timezone.now().date() >= self.release_date


class S3ExpiringModelMixin(models.Model):
    url_last_fetched = models.DateTimeField(null=True, blank=True)
    url_last_error = models.DateTimeField(null=True, blank=True)
    url = models.CharField(max_length=300, null=True, blank=True)

    class Meta:
        abstract = True

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
            if self.match_required and self.name.lower() in (names := get_song_names(S3Client().client, self.project)):
                self.url = get_presigned_url(S3Client().client, names[self.name.lower()])
                self.url_last_fetched = timezone.now()
            elif not self.match_required:
                self.url = get_presigned_url(S3Client().client, self.name)
                self.url_last_fetched = timezone.now()
            else:
                self.url_last_error = timezone.now()
            self.save()
        return self.url


class Song(S3ExpiringModelMixin, LockableModel):
    match_required = True
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    sync_enabled = models.BooleanField(default=True)
    directory_name = models.CharField(max_length=200, null=True, blank=True,
                                      help_text="Specify a different folder name for Syncprojects-client to use ("
                                                "optional)")
    project_file = models.CharField(max_length=200, null=True, blank=True, help_text="By default, the most recently "
                                                                                     "edited .cpr file is opened. Use"
                                                                                     "this to supply a custom "
                                                                                     "filename.")
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
    links = GenericRelation(Link)
    show_in_player = models.BooleanField(default=True)

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
        return self.sync_set.all().count()

    def last_audio_sync(self):
        from sync.models import AudioSync
        return AudioSync.objects.filter(song=self).last()

    def unresolved_comments(self):
        return self.comment_set.filter(
            Q(requires_resolution=True, resolved=False, hidden=False) | Q(requires_resolution=False, hidden=False))


class FeatureChangelog(models.Model):
    date = models.DateField(default=timezone.now)
    changes = models.TextField()

    def __str__(self):
        return str(self.date)

    def format_changes(self):
        return re.sub(r'((^|\n)##?) ', r'\1##', self.changes)
