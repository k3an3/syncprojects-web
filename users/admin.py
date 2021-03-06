from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group

from users.models import User


class UserProjectInline(admin.TabularInline):
    model = User.projects.through
    can_delete = False
    verbose_name_plural = "user"


class UserAdmin(BaseUserAdmin):
    add_fieldsets = ((None, {'classes': ('wide',), 'fields': ('email', 'password1', 'password2')}),)
    fieldsets = (*BaseUserAdmin.fieldsets,
                 ('Profile',
                  {'fields': ('profile_picture',
                              'bio',
                              'instruments',
                              'genres_musical_taste',
                              'open_to_collaboration',
                              'private')}),
                 ('Projects',
                  {'fields': ('projects', 'subscribed_projects', 'collab_songs')})
                 )


admin.site.register(User, UserAdmin)
admin.site.unregister(Group)
