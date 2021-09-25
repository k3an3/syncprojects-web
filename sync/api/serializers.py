from django.utils import timezone
from rest_framework import serializers

from sync.models import ChangelogEntry, Sync, SupportedClientTarget, ClientUpdate, ClientLog


class ChangelogEntrySerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = ChangelogEntry
        fields = ["id", "text", "song", "date_created", "user"]

    def get_user(self, changelog):
        return changelog.user.display_name()


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
