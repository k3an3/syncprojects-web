import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils.html import escape

PARTY_GROUP = "party"


def get_group(key: int):
    return '_'.join((PARTY_GROUP, str(key)))


# noinspection PyAttributeOutsideInit
class PartyConsumer(AsyncWebsocketConsumer):
    @database_sync_to_async
    def check_song_access(self, song_id):
        from core.models import Song
        song = Song.objects.get(id=int(song_id))
        if self.user.can_sync(song):
            return True
        return False

    @database_sync_to_async
    def check_project_access(self, proj_id):
        from core.models import Project
        proj = Project.objects.get(id=int(proj_id))
        if self.user.can_sync(proj):
            return True
        return False

    async def connect(self):
        self.user = self.scope["user"]
        self.song = self.scope["url_route"]["kwargs"].get("song")
        self.project = self.scope["url_route"]["kwargs"].get("project")
        if self.song:
            if not await self.check_song_access(self.song):
                await self.close()
        else:
            if not await self.check_project_access(self.project):
                await self.close()
        item = self.song if self.song else self.project
        await self.channel_layer.group_send(
            get_group(item),
            {
                'type': 'action',
                'message': {'user': escape(self.user.display_name()), 'action': 'join'}
            }
        )
        await self.channel_layer.group_add(
            get_group(item),
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            get_group(self.song),
            self.channel_name
        )
        item = self.song if self.song else self.project
        await self.channel_layer.group_send(
            get_group(item),
            {
                'type': 'action',
                'message': {'user': escape(self.user.display_name()), 'action': 'quit'}
            }
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        data['user'] = escape(self.user.display_name())

        # Send message to room group
        item = self.song if self.song else self.project
        await self.channel_layer.group_send(
            get_group(item),
            {
                'type': 'action',
                'message': data
            }
        )

    # Receive message from room group
    async def action(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps(
            message
        ))
