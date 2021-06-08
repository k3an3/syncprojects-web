from django.contrib import admin

from sync.models import Sync, ClientUpdate, ChangelogEntry, SupportedClientTarget

admin.site.register(Sync)
admin.site.register(ClientUpdate)
admin.site.register(ChangelogEntry)
admin.site.register(SupportedClientTarget)
