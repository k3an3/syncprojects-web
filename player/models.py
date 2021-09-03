from django.db import models

from core.models import Song


class SongRegion(models.Model):
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    start = models.DurationField()
    end = models.DurationField()
    name = models.CharField(max_length=50)
    color = models.PositiveIntegerField()
