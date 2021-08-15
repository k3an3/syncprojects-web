from django.contrib import admin

from sync.models import Sync, ClientUpdate, ChangelogEntry, SupportedClientTarget, ClientLog, AudioSync

admin.site.register(Sync)
admin.site.register(ClientUpdate)
admin.site.register(ChangelogEntry)
admin.site.register(SupportedClientTarget)
admin.site.register(ClientLog)
admin.site.register(AudioSync)
