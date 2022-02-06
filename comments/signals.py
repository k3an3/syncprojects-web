from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse

from comments.models import Comment, CommentLike
from notifications.consumers import NotifyConsumer


@receiver(post_save, sender=Comment)
def comment_handler(sender, instance, **kwargs):
    if instance.song:
        name = instance.song.name
        url = reverse('core:song-detail', args=(instance.song.project.id, instance.song.id))
    else:
        name = instance.project.name
        url = reverse('core:project-detail', args=(instance.project.id,))
    msg = f"{instance.user.display_name()} commented on <a href=\"{url}#comment-{instance.id}\">{name}</a>"
    NotifyConsumer.send_notification(instance.project.id, instance.user.id, "Comments", msg)


@receiver(post_save, sender=CommentLike)
def comment_like_handler(sender, instance, **kwargs):
    if instance.comment.song:
        url = reverse('core:song-detail', args=(instance.comment.song.project.id, instance.comment.song.id))
    else:
        url = reverse('core:project-detail', args=(instance.comment.project.id,))
    msg = f"{instance.user.display_name()} liked your <a href=\"{url}#comment-{instance.id}\">comment</a>"
    NotifyConsumer.send_notification(instance.comment.project.id, instance.user.id, "Comments", msg)
