from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic

from core.models import Project, Song
from core.permissions import UserHasObjectPermissionMixin


class IndexView(LoginRequiredMixin, generic.ListView):
    def get_queryset(self):
        return Project.objects.order_by('-name')


class ProjectDetailView(LoginRequiredMixin, UserHasObjectPermissionMixin, generic.DetailView):
    model = Project

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['songs'] = self.get_object().songs()
        return context


class SongDetailView(LoginRequiredMixin, UserHasObjectPermissionMixin, generic.DetailView):
    model = Song

    def get_object(self, queryset=None):
        return Song.objects.get(id=self.kwargs['song'], project=self.kwargs['proj'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = self.get_object().project
        return context
