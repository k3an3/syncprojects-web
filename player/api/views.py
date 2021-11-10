from rest_framework import viewsets, permissions

from api.permissions import UserHasProjectAccess
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
                return SongRegion.objects.none()
            if not self.request.user.can_sync(song):
                return SongRegion.objects.none()
            return SongRegion.objects.filter(song=song)
        return SongRegion.objects.all()
