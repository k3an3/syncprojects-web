from django.contrib.auth.models import User, Group
from rest_framework import serializers

from core.models import Project, Song
from sync.models import Sync, Lock


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']


class SongSerializer(serializers.ModelSerializer):
    class Meta:
        model = Song
        fields = "__all__"


class LockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lock
        fields = "__all__"


class SyncSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sync
        fields = "__all__"


class ProjectSerializer(serializers.ModelSerializer):
    is_locked = serializers.BooleanField(read_only=True)
    songs = SongSerializer(many=True, read_only=True)
    locks = LockSerializer(many=True, read_only=True)
    syncs = SyncSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = "__all__"
