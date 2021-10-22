import re

from rest_framework import serializers

from snippets.models import Snippet


class SnippetSerializer(serializers.ModelSerializer):
    upload_url = serializers.ReadOnlyField()
    name = serializers.CharField()

    @staticmethod
    def validate_name(name):
        if not re.match(r'.*\.(mp3|ogg|wav|flac|m4a)', name, re.IGNORECASE):
            raise serializers.ValidationError('The file must be of supported type.')
        return name

    class Meta:
        model = Snippet
        fields = ['project', 'name', 'upload_url', 'id']
