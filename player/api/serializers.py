from rest_framework import serializers

from player.models import SongRegion


class SongRegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SongRegion
        fields = ['id', 'start', 'end', 'name', 'color', 'song']
