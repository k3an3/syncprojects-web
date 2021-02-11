from django.contrib import admin

from core.models import Project, Song, Lock, Sync

for model in (Lock, Sync):
    admin.site.register(model)


class ProjectAdmin(admin.ModelAdmin):
    fields = ['name']


class SongAdmin(admin.ModelAdmin):
    fields = ['name', 'url']


admin.site.register(Project, ProjectAdmin)
admin.site.register(Song, SongAdmin)
