# chat/consumers.py
import json
from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer

NOTIFY_GROUP = "notify"


def get_group(key: int):
    return '_'.join((NOTIFY_GROUP, str(key)))


# noinspection PyAttributeOutsideInit
class NotifyConsumer(AsyncWebsocketConsumer):
    @database_sync_to_async
    def get_projects(self):
        return [project.id for project in self.user.projects.all()]

    async def connect(self):
        self.user = self.scope["user"]
        self.projects = await self.get_projects()
        for project in self.projects:
            await self.channel_layer.group_add(
                get_group(project),
                self.channel_name
            )

        await self.accept()

    async def disconnect(self, close_code):
        for project in self.projects:
            await self.channel_layer.group_discard(
                get_group(project),
                self.channel_name
            )

    async def notify_message(self, event):
        message = event['message']
        if event['user'] != self.user.id:
            await self.send(text_data=json.dumps(message))

    @staticmethod
    def send_notification(project, subject, title, content, color_class="default", icon=""):
        """
        Called from external, non-async contexts
        """
        async_to_sync(get_channel_layer().group_send)(
            get_group(project),
            {
                'type': 'notify.message',
                'message': {
                    'title': title,
                    'content': content,
                    'type': color_class,
                    'icon': icon,
                },
                'user': subject,
            }
        )
