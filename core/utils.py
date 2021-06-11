from sync.models import ChangelogEntry


def get_syncs(obj, count: int = 10):
    for sync in obj.sync_set.all().order_by('-id')[:count]:
        try:
            changelog = sync.changelog.get(song=obj.id)
        except ChangelogEntry.DoesNotExist:
            changelog = None
        yield sync, changelog


def safe_append(d: dict, key: str, item) -> None:
    try:
        d[key].append(item)
    except KeyError:
        d[key] = [item]
