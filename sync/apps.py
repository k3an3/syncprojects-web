from django.apps import AppConfig


class SyncConfig(AppConfig):
    name = 'sync'

    def ready(self):
        # noinspection PyUnresolvedReferences
        import sync.signals
