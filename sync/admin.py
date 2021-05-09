from django.contrib import admin

from sync.models import Sync, ClientUpdate, ChangelogEntry

admin.site.register(Sync)
admin.site.register(ClientUpdate)
admin.site.register(ChangelogEntry)
