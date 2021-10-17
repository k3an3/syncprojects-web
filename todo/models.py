from django.db import models
from django.utils import timezone

from core.models import Project, Song
from syncprojectsweb.settings import AUTH_USER_MODEL


class Todo(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    song = models.ForeignKey(Song, null=True, blank=True, on_delete=models.CASCADE, help_text="Optional")
    assignee = models.ForeignKey(AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE, help_text="Optional")
    created = models.DateTimeField(default=timezone.now)
    due = models.DateTimeField(null=True, blank=True, help_text="Optional; YYYY-MM-DD")
    done = models.BooleanField(default=False)
    text = models.TextField()

    def __str__(self):
        return self.project.name + " " + self.text
