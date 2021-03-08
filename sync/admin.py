from django.contrib import admin

# Register your models here.
from sync.models import Sync, ClientUpdate

admin.site.register(Sync)
admin.site.register(ClientUpdate)
