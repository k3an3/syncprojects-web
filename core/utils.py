from sync.models import ChangelogEntry


def get_syncs(obj, count: int = 10):
    for sync in obj.sync_set.all().order_by('-id')[:count]:
        try:
            changelog = sync.changelog.get(song=obj.id)
        except ChangelogEntry.DoesNotExist:
            changelog = None
        yield sync, changelog
