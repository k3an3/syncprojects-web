from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from core.models import Project, Song, CoreUser
from sync.models import Sync, Lock

for model in (Lock, Sync):
    admin.site.register(model)


class SongAdmin(admin.ModelAdmin):
    fields = ['name', 'url', 'project', 'directory_name', 'sync_enabled']


class CoreUserInline(admin.StackedInline):
    model = CoreUser
    can_delete = False
    verbose_name_plural = "core user"


class CoreUserProjectInline(admin.TabularInline):
    model = CoreUser.projects.through
    can_delete = False
    verbose_name_plural = "core user"


class UserAdmin(BaseUserAdmin):
    inlines = (CoreUserInline,)


class ProjectAdmin(admin.ModelAdmin):
    fields = ['name', 'image']
    inlines = (CoreUserProjectInline,)


admin.site.site_header = 'Syncprojects Admin'
admin.site.site_title = 'Syncprojects Administration'
admin.site.register(Project, ProjectAdmin)
admin.site.register(Song, SongAdmin)
# Use custom user inline
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
