from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers

from core.models import Project, Song, Lock
from sync.models import Sync, ClientUpdate, ChangelogEntry, ClientLog, SupportedClientTarget


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['url', 'username']


class LockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lock
        fields = "__all__"


class ChangelogEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = ChangelogEntry
        fields = ["id", "text", "song"]


class SyncSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    sync_time = serializers.DateTimeField(
        read_only=True,
        default=timezone.now()
    )
    changelog = ChangelogEntrySerializer(read_only=True, many=True)

    class Meta:
        model = Sync
        fields = ["user", "sync_time", "changelog", "project", "songs"]

    def get_changelogs(self, sync):
        return ChangelogEntrySerializer(sync.changelog, many=True).data


class SongSerializer(serializers.ModelSerializer):
    is_locked = serializers.BooleanField(read_only=True)

    class Meta:
        model = Song
        fields = ["id", "name", "created_at", "updated_at", "sync_enabled", "directory_name", "last_mtime", "project",
                  "is_locked", "revision", "url"]


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


class ClientUpdateSerializer(serializers.ModelSerializer):
    updater = serializers.SerializerMethodField(read_only=True)
    target = serializers.SlugRelatedField(slug_field='target', queryset=SupportedClientTarget.objects.all())

    class Meta:
        model = ClientUpdate
        fields = ["version", "updater", "package", "target"]

    def get_updater(self, client_update):
        request = self.context.get('request')
        url = client_update.latest_updater()
        return request.build_absolute_uri(url)


class ClientLogSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = ClientLog
        fields = "__all__"
