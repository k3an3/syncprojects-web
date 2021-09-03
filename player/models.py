from django.core.validators import MinValueValidator
from django.db import models

from core.models import Song


class SongRegion(models.Model):
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    start = models.FloatField(validators=[MinValueValidator(0.0)])
    end = models.FloatField(validators=[MinValueValidator(0.0)])
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=6)

    def __str__(self):
        return f"{self.name} ({self.song.name} - {self.start:.2f}-{self.end:.2f})"
