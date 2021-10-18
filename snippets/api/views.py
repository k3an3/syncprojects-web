from rest_framework import viewsets

from api.views import HTTP_404_RESPONSE, HTTP_403_RESPONSE
from core.models import Project
from snippets.api.serializers import SnippetSerializer
from snippets.models import Snippet


class SnippetViewSet(viewsets.ModelViewSet):
    serializer_class = SnippetSerializer

    def get_queryset(self):
        return Snippet.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        try:
            project = Project.objects.get(id=self.request.data['project'])
        except Project.DoesNotExist:
            return HTTP_404_RESPONSE
        if not self.request.user.can_sync(project):
            return HTTP_403_RESPONSE
        serializer.save(user=self.request.user, project=project)
