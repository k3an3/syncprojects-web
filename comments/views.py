from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse
from django.views import generic

from comments.models import Comment
from core.models import Project, Song


class CommentCreateView(LoginRequiredMixin, generic.CreateView):
    model = Comment
    fields = ['text', 'assignee', 'song_time']

    def form_valid(self, form):
        project = Project.objects.get(pk=self.kwargs.get('proj'))
        if 'song' in self.kwargs:
            song = Song.objects.get(pk=self.kwargs.get('song'))
            form.instance.song = song
        form.instance.project = project
        form.instance.user = self.request.user
        form.instance.save()
        return super().form_valid(form)

    def get_success_url(self):
        if self.object.song:
            return reverse('core:song-detail', args=[self.object.project.pk, self.object.song.pk])
        return reverse('core:project-detail', args=[self.object.project.pk])


class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, generic.DeleteView):
    model = Comment

    def test_func(self):
        return self.get_object().user == self.request.user

    def get_success_url(self):
        if self.object.song:
            return reverse('core:song-detail', args=[self.object.project.pk, self.object.song.pk])
        return reverse('core:project-detail', args=[self.object.project.pk])