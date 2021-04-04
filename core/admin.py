from django.contrib import admin

from core.models import Project, Song, Lock
from users.admin import UserProjectInline

admin.site.register(Lock)


class SongAdmin(admin.ModelAdmin):
    fields = ['name', 'url', 'project', 'directory_name', 'sync_enabled', 'shared_with_followers']


class ProjectAdmin(admin.ModelAdmin):
    fields = ['name', 'image', 'sync_enabled', 'seafile_uuid']
    inlines = (UserProjectInline,)


admin.site.site_header = 'Syncprojects Admin'
admin.site.site_title = 'Syncprojects Administration'
admin.site.register(Project, ProjectAdmin)
admin.site.register(Song, SongAdmin)
