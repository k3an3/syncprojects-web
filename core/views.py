from django.views import generic

from core.models import Project, Song


class IndexView(generic.ListView):
    def get_queryset(self):
        return Project.objects.order_by('-name')


class ProjectDetailView(generic.DetailView):
    model = Project


class SongDetailView(generic.DetailView):
    model = Song
