from django.contrib import admin

from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from core.models import Project, Song, Lock, Sync, CoreUser

for model in (Lock, Sync):
    admin.site.register(model)


class ProjectAdmin(admin.ModelAdmin):
    fields = ['name']


class SongAdmin(admin.ModelAdmin):
    fields = ['name', 'url']


class CoreUserInline(admin.StackedInline):
    model = CoreUser
    can_delete = False
    verbose_name_plural = "core user"


class UserAdmin(BaseUserAdmin):
    inlines = (CoreUserInline,)


admin.site.register(Project, ProjectAdmin)
admin.site.register(Song, SongAdmin)
# Use custom user inline
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
