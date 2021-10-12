from rest_framework import viewsets

from snippets.api.serializers import SnippetSerializer


class SnippetViewSet(viewsets.ModelViewSet):
    serializer_class = SnippetSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
