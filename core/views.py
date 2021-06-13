from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.views import generic, View
from django.views.generic.detail import SingleObjectMixin

from core.forms import AlbumForm
from core.models import Project, Song, Album, FeatureChangelog
from core.permissions import UserIsMemberPermissionMixin, UserIsFollowerOrMemberPermissionMixin
from core.utils import get_syncs


class IndexView(LoginRequiredMixin, generic.ListView):
    def get_queryset(self):
        return self.request.user.projects.order_by('-name')

    def get_context_data(self, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['subscribed_projects_list'] = self.request.user.subscribed_projects.all()
        if self.request.user.latest_feature_seen != FeatureChangelog.objects.last():
            context['changes'] = FeatureChangelog.objects.all()
            self.request.user.latest_feature_seen = FeatureChangelog.objects.last()
            self.request.user.save()
        return context


class ProjectDetailView(LoginRequiredMixin, UserIsFollowerOrMemberPermissionMixin, generic.DetailView):
    model = Project

    def _song_is_visible(self, song):
        return (self.request.user.has_member_access(song)
                or song.shared_with_followers
                or self.request.user.can_sync(song))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.get_object()
        # Collect songs without albums
        albums = [(None, [song for song in project.song_set.filter(album__isnull=True) if self._song_is_visible(song)])]
        member = self.request.user.has_member_access(project)
        if album_filter := self.request.GET.get('album'):
            context['filtered'] = True
            if not album_filter == 'unsorted':
                album_set = project.album_set.filter(id=album_filter)
                # Don't need unsorted if filtering
                albums = []
            else:
                album_set = project.album_set.none()
        else:
            album_set = project.album_set.all()
        for album in album_set:
            songs = []
            for song in album.song_set.order_by('-album_order'):
                if self._song_is_visible(song):
                    songs.append(song)
            # Don't show albums that a subscriber has no song access to
            if member or songs:
                albums.append((album, songs))
        context['albums'] = albums
        context['member'] = member
        context['subscriber'] = self.request.user.has_subscriber_access(project)
        context['collab'] = self.request.user.collab_songs.filter(project=project)
        if context['member']:
            context['syncs'] = project.sync_set.all().order_by('-id')[:10]
        return context


class ProjectCreateView(LoginRequiredMixin, generic.CreateView):
    model = Project
    fields = ['name', 'image', 'sync_enabled']

    def form_valid(self, form):
        obj = form.save()
        self.request.user.projects.add(obj)
        return super().form_valid(form)


class ProjectUpdateView(UserIsMemberPermissionMixin, generic.UpdateView):
    model = Project
    fields = ['name', 'image', 'sync_enabled']
    template_name_suffix = '_update_form'


class ProjectDeleteView(LoginRequiredMixin, UserIsMemberPermissionMixin, generic.DeleteView):
    model = Project
    success_url = reverse_lazy('core:index')


class ProjectUnsubscribeView(LoginRequiredMixin, UserPassesTestMixin, SingleObjectMixin, View):
    model = Project

    def test_func(self):
        return self.request.user.has_subscriber_access(self.get_object())

    def post(self, *args, **kwargs):
        self.request.user.subscribed_projects.remove(self.get_object())
        return redirect(reverse('core:index'))


class ProjectCreateBaseView(LoginRequiredMixin, UserPassesTestMixin, generic.CreateView):
    def get_success_url(self):
        return reverse('core:project-detail', args=(self.kwargs['pk'],))

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


class SongCreateView(ProjectCreateBaseView):
    model = Song
    fields = ['name', 'sync_enabled', 'directory_name', 'shared_with_followers', 'album', 'album_order']


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
            context['syncs'] = get_syncs(self.get_object())
        return context


class SongUpdateView(SongLookupBaseView, UserIsMemberPermissionMixin, generic.UpdateView):
    model = Song
    fields = ['name', 'sync_enabled', 'directory_name', 'shared_with_followers', 'album', 'album_order']
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
        return reverse('core:project-detail', args=[self.object.project.pk])


class RegenSongURLView(SongLookupBaseView, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_superuser

    def get(self, *args, **kwargs):
        song = self.get_object()
        song.url_last_fetched = None
        song.signed_url
        return redirect('core:song-detail', song.project.id, song.id)


class AlbumLookupBaseView(LoginRequiredMixin, UserIsMemberPermissionMixin):
    model = Album

    def get_object(self, queryset=None):
        return Album.objects.get(id=self.kwargs['album'], project=self.kwargs['proj'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = self.get_object().project
        return context


class AlbumSongView:
    model = Album
    form_class = AlbumForm

    def get_success_url(self):
        return reverse('core:project-detail', args=[self.object.project.pk])

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['songs'].queryset = Project.objects.get(
            id=self.kwargs.get('pk', self.kwargs.get('proj'))).song_set.all()
        if form.instance:
            form.fields['songs'].initial = form.instance.song_set.all()
        return form

    def form_valid(self, form):
        project = Project.objects.get(pk=self.kwargs.get('pk', self.kwargs.get('proj')))
        original_songs = form.instance.song_set.all()
        form.instance.project = project
        form.instance.save()
        for song in form.cleaned_data['songs']:
            if song.project == project:
                song.album = form.instance
                song.save()
        for song in original_songs.exclude(id__in=form.cleaned_data['songs']):
            song.album = None
            song.save()
        return super().form_valid(form)


class AlbumCreateView(AlbumSongView, ProjectCreateBaseView):
    pass


class AlbumUpdateView(AlbumLookupBaseView, AlbumSongView, generic.UpdateView):
    template_name_suffix = '_update_form'


class AlbumDeleteView(AlbumLookupBaseView, generic.DeleteView):
    def get_success_url(self):
        return reverse('core:project-detail', args=[self.object.project.pk])
