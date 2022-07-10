from rest_framework import serializers

from core.models import Project, Song, Lock, Album
from sync.api.serializers import SyncSerializer


class LockSerializer(serializers.ModelSerializer):
    start_time = serializers.SerializerMethodField()

    class Meta:
        model = Lock
        fields = "__all__"

    @staticmethod
    def get_start_time(lock):
        return lock.start_time.timestamp()


class SongSerializer(serializers.ModelSerializer):
    is_locked = serializers.BooleanField(read_only=True)

    class Meta:
        model = Song
        fields = ["id", "name", "created_at", "updated_at", "sync_enabled", "directory_name", "last_mtime", "project",
                  "is_locked", "revision", "url", "archived", "project_file", "album", "album_order"]


class ProjectSerializer(serializers.ModelSerializer):
    is_locked = serializers.BooleanField(read_only=True)
    songs = serializers.SerializerMethodField()
    syncs = SyncSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = "__all__"

    def get_songs(self, project):
        request = self.context.get('request')
        if request.user.has_member_access(project):
            return SongSerializer(project.songs(), many=True, read_only=True).data
        return SongSerializer(request.user.collab_songs.filter(project=project), many=True, read_only=True).data


class AlbumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Album
        fields = "__all__"
