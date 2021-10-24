from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import F
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views import generic

from core.models import Project
from core.permissions import UserCanSyncMixin
from todo.models import Todo

TODO_FIELDS = ['song', 'assignee', 'due', 'text']


class ProjectContextMixin(UserPassesTestMixin):
    def test_func(self):
        project = get_object_or_404(Project, id=self.kwargs['project'])
        return self.request.user.can_sync(project)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        project = get_object_or_404(Project, id=self.kwargs['project'])
        context['project'] = project
        context['member'] = self.request.user.has_member_access(project)
        return context


class TodoListView(LoginRequiredMixin, ProjectContextMixin, generic.ListView):
    model = Todo

    def get_queryset(self):
        project = get_object_or_404(Project, id=self.kwargs['project'])
        return project.todo_set.order_by('done', F('due').asc(nulls_last=True))


class TodoCreateView(LoginRequiredMixin, ProjectContextMixin, generic.CreateView):
    model = Todo
    fields = TODO_FIELDS

    def get_success_url(self):
        return reverse('todo:list-todo', args=[self.object.project.pk])

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['song'].queryset = Project.objects.get(
            id=self.kwargs['project']).song_set.all()
        if form.instance:
            form.fields['song'].initial = form.instance.song
        return form

    def form_valid(self, form):
        project = Project.objects.get(pk=self.kwargs['project'])
        form.instance.project = project
        form.instance.save()
        return super().form_valid(form)


class TodoDeleteView(LoginRequiredMixin, UserCanSyncMixin, generic.DeleteView):
    model = Todo

    def get_success_url(self):
        return reverse('todo:list-todo', args=[self.object.project.pk])


class TodoUpdateView(LoginRequiredMixin, UserCanSyncMixin, generic.UpdateView):
    model = Todo
    fields = TODO_FIELDS

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['song'].queryset = form.instance.project.song_set.all()
        if form.instance:
            form.fields['song'].initial = form.instance.song
        return form

    def get_success_url(self):
        return reverse('todo:list-todo', args=[self.object.project.pk])
