from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views import generic, View

from core.models import Project, Song
from core.permissions import UserHasObjectPermissionMixin


class IndexView(LoginRequiredMixin, generic.ListView):
    def get_queryset(self):
        return self.request.user.coreuser.projects.order_by('-name')


class ProjectDetailView(LoginRequiredMixin, UserHasObjectPermissionMixin, generic.DetailView):
    model = Project

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['songs'] = self.get_object().songs()
        return context


class SongLookupBaseView(LoginRequiredMixin, UserHasObjectPermissionMixin):
    model = Song

    def get_object(self, queryset=None):
        return Song.objects.get(id=self.kwargs['song'], project=self.kwargs['proj'])


class SongDetailView(SongLookupBaseView, generic.DetailView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = self.get_object().project
        return context


class ClearSongPeaksView(SongLookupBaseView, View):
    def get(self, *args, **kwargs):
        song = self.get_object()
        song.clear_peaks()
        return redirect('core:song_detail', song.project.id, song.id)
