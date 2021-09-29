from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.views import generic

from core.models import Project, Song
from snippets.models import Snippet


class SnippetListView(LoginRequiredMixin, generic.ListView):
    model = Snippet

    def get_queryset(self):
        if 'project' in self.kwargs:
            obj = get_object_or_404(Project, id=self.kwargs['project'])
        elif 'song' in self.kwargs:
            obj = get_object_or_404(Song, id=self.kwargs['song'])
        else:
            return Snippet.objects.none()

        if not self.request.user.can_sync(obj):
            # better to use UserPassesTest?
            raise PermissionDenied()

        return obj.snippets.all()
