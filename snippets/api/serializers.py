from rest_framework import serializers

from snippets.models import Snippet


class SnippetSerializer(serializers.ModelSerializer):
    upload_url = serializers.ReadOnlyField()

    class Meta:
        model = Snippet
        fields = ['project', 'name', 'upload_url', 'id']
