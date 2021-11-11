from rest_framework import serializers

from comments.models import Comment, Tag


class CommentSerializer(serializers.ModelSerializer):
    edited = serializers.ReadOnlyField()
    posted_date = serializers.DateTimeField(read_only=True)
    song_time_seconds = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ["id", "text", "song_time", "song_time_seconds", "assignee",
                  "edited", "project", "song", "posted_date",
                  "requires_resolution", "resolved", "parent"]

    @staticmethod
    def get_song_time_seconds(comment):
        if comment.song_time:
            return comment.song_time.total_seconds()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['name']
