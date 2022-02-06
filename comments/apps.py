from django.apps import AppConfig


class CommentsConfig(AppConfig):
    name = 'comments'

    def ready(self):
        # noinspection PyUnresolvedReferences
        import comments.signals
