from django.contrib.auth.models import AbstractUser
from django.db import models

from core.models import Project, Song
from sync.models import Sync


class User(AbstractUser):
    email = models.EmailField(max_length=254, unique=True)
    projects = models.ManyToManyField(Project, blank=True)
    subscribed_projects = models.ManyToManyField(Project, blank=True, related_name="subscribed_projects")
    profile_picture = models.ImageField(null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    instruments = models.TextField(null=True, blank=True)
    genres_musical_taste = models.TextField(null=True, blank=True, verbose_name="Genres and Musical Taste")
    open_to_collaboration = models.BooleanField(default=False)
    private = models.BooleanField(default=True,
                                  help_text="Profiles of private accounts will have their details hidden.")

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'auth_user'

    # TODO: social_links

    @staticmethod
    def check_object_access(obj, projects):
        if isinstance(obj, Project):
            try:
                return projects.get(id=obj.id)
            except Project.DoesNotExist:
                return False
        elif isinstance(obj, Song):
            try:
                return projects.get(id=obj.project.id)
            except Project.DoesNotExist:
                return False
        elif isinstance(obj, Sync):
            return obj.project in projects.all()
        else:
            raise NotImplementedError()

    def has_member_access(self, obj):
        return self.check_object_access(obj, self.projects)

    def has_subscriber_access(self, obj):
        return self.check_object_access(obj, self.subscribed_projects)

    def __str__(self):
        return self.first_name or self.username
