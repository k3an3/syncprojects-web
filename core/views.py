from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic

from core.models import Project, Song
from core.permissions import UserHasObjectPermissionMixin


class IndexView(LoginRequiredMixin, generic.ListView):
    def get_queryset(self):
        return Project.objects.order_by('-name')


class ProjectDetailView(LoginRequiredMixin, UserHasObjectPermissionMixin, generic.DetailView):
    model = Project


class SongDetailView(LoginRequiredMixin, UserHasObjectPermissionMixin, generic.DetailView):
    model = Song
