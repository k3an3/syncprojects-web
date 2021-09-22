import timeago
from django.db import models
from django.utils import timezone

from core.models import Song, Project
from syncprojectsweb.settings import AUTH_USER_MODEL


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
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children', on_delete=models.SET_NULL)
    hidden = models.BooleanField(default=False)

    def hide_tree(self):
        for comment in self.tree():
            comment.hidden = True
            comment.save()
            comment.hide_tree()

    def tree(self):
        return self.children.all()

    def is_root(self):
        return self.parent is None

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

    @property
    def likes(self):
        return self.commentlike_set.all().count()

    def liked_by(self, user):
        try:
            return self.commentlike_set.get(user=user)
        except CommentLike.DoesNotExist:
            return None


class CommentLike(models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)