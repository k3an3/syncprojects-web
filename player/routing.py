from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/party/song/(?P<song>\d+)/$', consumers.PartyConsumer.as_asgi()),
    re_path(r'ws/party/project/(?P<project>\d+)/$', consumers.PartyConsumer.as_asgi()),
]
