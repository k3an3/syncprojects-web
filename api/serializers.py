from django.contrib.auth.models import User, Group
from rest_framework import serializers

from core.models import Project, Song, Lock


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


class ProjectSerializer(serializers.HyperlinkedModelSerializer):
    is_locked = serializers.BooleanField()
    songs = SongSerializer(many=True)
    locks = LockSerializer(many=True)

    class Meta:
        model = Project
        fields = "__all__"
