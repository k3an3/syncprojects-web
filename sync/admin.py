from django.contrib import admin

import sync.models as models

admin.site.register(models.Sync)
admin.site.register(models.ClientUpdate)
admin.site.register(models.ChangelogEntry)
admin.site.register(models.SupportedClientTarget)
admin.site.register(models.ClientLog)
admin.site.register(models.AudioSync)
admin.site.register(models.ClientFeatureChangelog)
