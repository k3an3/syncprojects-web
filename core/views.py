from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
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


class ProjectCreateView(LoginRequiredMixin, generic.CreateView):
    model = Project
    fields = ['name', 'image', 'sync_enabled', 'seafile_uuid']

    def form_valid(self, form):
        obj = form.save()
        self.request.user.coreuser.projects.add(obj)
        return super().form_valid(form)


class ProjectUpdateView(generic.UpdateView):
    model = Project
    fields = ['name', 'image', 'sync_enabled', 'seafile_uuid']
    template_name_suffix = '_update_form'


class ProjectDeleteView(LoginRequiredMixin, UserHasObjectPermissionMixin, generic.DeleteView):
    model = Project
    success_url = reverse_lazy('core:index')


class SongCreateView(LoginRequiredMixin, UserPassesTestMixin, generic.CreateView):
    model = Song
    fields = ['name', 'url', 'sync_enabled', 'directory_name']

    def test_func(self, **kwargs):
        project = Project.objects.get(pk=self.kwargs['pk'])
        return self.request.user.coreuser.has_member_access(project)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = Project.objects.get(pk=self.kwargs['pk'])
        return context

    def form_valid(self, form):
        form.instance.project = Project.objects.get(pk=self.kwargs['pk'])
        return super().form_valid(form)


class SongLookupBaseView(LoginRequiredMixin, UserHasObjectPermissionMixin):
    model = Song

    def get_object(self, queryset=None):
        return Song.objects.get(id=self.kwargs['song'], project=self.kwargs['proj'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = self.get_object().project
        return context


class SongDetailView(SongLookupBaseView, generic.DetailView):
    pass


class SongUpdateView(SongLookupBaseView, generic.UpdateView):
    model = Song
    fields = ['name', 'url', 'sync_enabled', 'directory_name']
    template_name_suffix = '_update_form'


class ClearSongPeaksView(SongLookupBaseView, View):
    def get(self, *args, **kwargs):
        song = self.get_object()
        song.clear_peaks()
        return redirect('core:song-detail', song.project.id, song.id)


class SongDeleteView(SongLookupBaseView, generic.DeleteView):
    model = Song

    def get_success_url(self):
        return reverse_lazy('core:project-detail', args=[self.object.project.pk])
