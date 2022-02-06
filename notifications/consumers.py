# chat/consumers.py
import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from channels.layers import get_channel_layer

NOTIFY_GROUP = "notify"


class NotifyConsumer(WebsocketConsumer):
    def connect(self):
        async_to_sync(self.channel_layer.group_add)(
            NOTIFY_GROUP,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            NOTIFY_GROUP,
            self.channel_name
        )

    def notify_message(self, event):
        message = event['message']
        self.send(text_data=json.dumps(message))

    @staticmethod
    def send_notification(title, content, color_class="default", icon=""):
        async_to_sync(get_channel_layer().group_send)(
            NOTIFY_GROUP,
            {
                'type': 'notify.message',
                'message': {
                    'title': title,
                    'content': content,
                    'type': color_class,
                    'icon': icon,
                }
            }
        )
