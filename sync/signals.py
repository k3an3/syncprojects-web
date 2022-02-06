from django.db.models.signals import post_save
from django.dispatch import receiver

from core.models import Lock
from notifications.consumers import NotifyConsumer
from sync.models import Sync


@receiver(post_save, sender=Sync)
def sync_handler(sender, instance, **kwargs):
    msg = f"{instance.user.display_name()} just synced {len(instance.songs)} song(s) in project {instance.project.name}"
    NotifyConsumer.send_notification(instance.project.id, instance.user.id, "Sync", msg)


@receiver(post_save, sender=Lock)
def checkout_handler(sender, instance, **kwargs):
    if instance.reason == "Checked out":
        msg = f"{instance.user.display_name()} checked out {instance.object.name}"
        NotifyConsumer.send_notification(instance.project.id, instance.user.id, "Sync", msg)
