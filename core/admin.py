from django.contrib import admin

from core.models import Project, Song, Lock, Album, FeatureChangelog, Link
from users.admin import UserProjectInline

admin.site.register(Lock)
admin.site.register(Album)
admin.site.register(FeatureChangelog)
admin.site.register(Link)


class SongAdmin(admin.ModelAdmin):
    fields = ['name', 'url', 'project', 'album', 'directory_name', 'sync_enabled', 'shared_with_followers']


class ProjectAdmin(admin.ModelAdmin):
    fields = ['name', 'image', 'sync_enabled']
    inlines = (UserProjectInline,)


admin.site.site_header = 'Syncprojects Admin'
admin.site.site_title = 'Syncprojects Administration'
admin.site.register(Project, ProjectAdmin)
admin.site.register(Song, SongAdmin)
