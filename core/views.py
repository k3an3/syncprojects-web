from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import generic, View

from core.models import Project, Song
from core.permissions import UserIsMemberPermissionMixin, UserIsFollowerOrMemberPermissionMixin


class IndexView(LoginRequiredMixin, generic.ListView):
    def get_queryset(self):
        return self.request.user.projects.order_by('-name')

    def get_context_data(self, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['subscribed_projects_list'] = self.request.user.subscribed_projects.all()
        return context


class ProjectDetailView(LoginRequiredMixin, UserIsFollowerOrMemberPermissionMixin, generic.DetailView):
    model = Project

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['songs'] = [song for song in self.get_object().songs() if
                            self.request.user.has_member_access(song) or
                            song.shared_with_followers or
                            self.request.user.can_sync(song)]
        context['member'] = self.request.user.has_member_access(self.get_object())
        context['collab'] = self.request.user.collab_songs.filter(project=self.get_object())
        if context['member']:
            context['syncs'] = self.get_object().sync_set.all().order_by('-id')[:10]
        return context


class ProjectCreateView(LoginRequiredMixin, generic.CreateView):
    model = Project
    fields = ['name', 'image', 'sync_enabled', 'seafile_uuid']

    def form_valid(self, form):
        obj = form.save()
        self.request.user.projects.add(obj)
        return super().form_valid(form)


class ProjectUpdateView(UserIsMemberPermissionMixin, generic.UpdateView):
    model = Project
    fields = ['name', 'image', 'sync_enabled', 'seafile_uuid']
    template_name_suffix = '_update_form'


class ProjectDeleteView(LoginRequiredMixin, UserIsMemberPermissionMixin, generic.DeleteView):
    model = Project
    success_url = reverse_lazy('core:index')


class SongCreateView(LoginRequiredMixin, UserPassesTestMixin, generic.CreateView):
    model = Song
    fields = ['name', 'url', 'sync_enabled', 'directory_name', 'shared_with_followers']

    def test_func(self, **kwargs):
        project = Project.objects.get(pk=self.kwargs['pk'])
        return self.request.user.has_member_access(project)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = Project.objects.get(pk=self.kwargs['pk'])
        return context

    def form_valid(self, form):
        form.instance.project = Project.objects.get(pk=self.kwargs['pk'])
        return super().form_valid(form)


class SongLookupBaseView(LoginRequiredMixin):
    model = Song

    def get_object(self, queryset=None):
        return Song.objects.get(id=self.kwargs['song'], project=self.kwargs['proj'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = self.get_object().project
        return context


class SongDetailView(SongLookupBaseView, UserIsFollowerOrMemberPermissionMixin, generic.DetailView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['member'] = self.request.user.has_member_access(self.get_object())
        context['can_sync'] = self.request.user.can_sync(self.get_object())
        if context['can_sync']:
            context['syncs'] = self.get_object().sync_set.all().order_by('-id')[:10]
        return context


class SongUpdateView(SongLookupBaseView, UserIsMemberPermissionMixin, generic.UpdateView):
    model = Song
    fields = ['name', 'url', 'sync_enabled', 'directory_name', 'shared_with_followers']
    template_name_suffix = '_update_form'


class ClearSongPeaksView(SongLookupBaseView, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_superuser

    def get(self, *args, **kwargs):
        song = self.get_object()
        song.clear_peaks()
        return redirect('core:song-detail', song.project.id, song.id)


class SongDeleteView(SongLookupBaseView, UserIsMemberPermissionMixin, generic.DeleteView):
    model = Song

    def get_success_url(self):
        return reverse_lazy('core:project-detail', args=[self.object.project.pk])
