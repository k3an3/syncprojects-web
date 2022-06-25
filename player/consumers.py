import json

from channels.db import database_sync_to_async
from core.models import Song
from channels.generic.websocket import AsyncWebsocketConsumer

PARTY_GROUP = "party"


def get_group(key: int):
    return '_'.join((PARTY_GROUP, str(key)))


# noinspection PyAttributeOutsideInit
class PartyConsumer(AsyncWebsocketConsumer):
    @database_sync_to_async
    def check_song_access(self, song_id):
        song = Song.objects.get(id=int(song_id))
        if self.user.can_sync(song):
            return True
        return False

    async def connect(self):
        self.user = self.scope["user"]
        self.song = self.scope["url_route"]["kwargs"]["song"]
        if not await self.check_song_access(self.song):
            await self.close()
        await self.channel_layer.group_add(
            get_group(self.song),
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            get_group(self.song),
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        data['user'] = self.user.username
        message = data['message']

        # Send message to room group
        await self.channel_layer.group_send(
            get_group(self.song),
            {
                'type': 'action',
                'message': message
            }
        )

    # Receive message from room group
    async def action(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps(
            message
        ))
