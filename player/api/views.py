from rest_framework import viewsets, permissions

from api.permissions import UserHasProjectAccess
from api.views import HTTP_404_RESPONSE, HTTP_403_RESPONSE
from core.models import Song
from player.api.serializers import SongRegionSerializer
from player.models import SongRegion


class SongRegionViewSet(viewsets.ModelViewSet):
    serializer_class = SongRegionSerializer
    permission_classes = [permissions.IsAuthenticated, UserHasProjectAccess]

    def get_queryset(self):
        if song := self.request.query_params.get('song'):
            try:
                song = Song.objects.get(id=song)
            except Song.DoesNotExist:
                return HTTP_404_RESPONSE
            if not self.request.user.can_sync(song):
                return HTTP_403_RESPONSE
            return SongRegion.objects.filter(song=song)
        return SongRegion.objects.none()
