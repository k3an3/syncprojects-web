from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views import generic

from core.models import Project
from snippets.models import Snippet


class SnippetListView(LoginRequiredMixin, generic.ListView):
    model = Snippet

    def get_queryset(self):
        project = get_object_or_404(Project, id=self.kwargs['project'])

        if not self.request.user.can_sync(project):
            # better to use UserPassesTest?
            raise Snippet.objects.none()

        return project.snippet_set.order_by('-id')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        project = get_object_or_404(Project, id=self.kwargs['project'])
        context['project'] = project
        context['member'] = self.request.user.has_member_access(project)
        return context


class SnippetDeleteView(LoginRequiredMixin, UserPassesTestMixin, generic.DeleteView):
    model = Snippet

    def get_success_url(self):
        return reverse('snippets:list-snippets', args=(self.get_object().project.id,))

    def test_func(self):
        return self.request.user.can_sync(self.get_object().project) or self.request.user.is_superuser
