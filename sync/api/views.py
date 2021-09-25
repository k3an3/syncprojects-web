from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response

from api.permissions import UserHasProjectAccess, CreateOrReadOnly, IsAdminOrWriteOnly
from api.views import HTTP_403_RESPONSE, HTTP_404_RESPONSE
from core.models import Song, Project
from sync.api.serializers import ClientUpdateSerializer, SyncSerializer, ChangelogEntrySerializer, ClientLogSerializer
from sync.models import SupportedClientTarget, ClientUpdate, Sync, ChangelogEntry, ClientLog, AudioSync
from syncprojectsweb.settings import BACKEND_ACCESS_ID, BACKEND_SECRET_KEY


class ClientUpdateViewSet(viewsets.ModelViewSet):
    serializer_class = ClientUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        target = self.request.query_params.get('target')
        if target:
            try:
                target = SupportedClientTarget.objects.get(target=target)
            except SupportedClientTarget.DoesNotExist:
                return ClientUpdate.objects.none()
            return ClientUpdate.objects.filter(target=target, visible=True)
        else:
            return ClientUpdate.objects.filter(target__isnull=True, visible=True)


class SyncViewSet(viewsets.ModelViewSet):
    serializer_class = SyncSerializer
    permission_classes = [permissions.IsAuthenticated, UserHasProjectAccess, CreateOrReadOnly]

    def get_queryset(self):
        song = self.request.query_params.get('song')
        revision = int(self.request.query_params.get('since_revision', 0))
        if not song:
            return Sync.objects.none()
        return Sync.objects.filter(songs=song)[revision:]

    def retrieve(self, request, pk=None):
        sync = super().retrieve(request, pk)
        sync.data['changelogs'] = ChangelogEntrySerializer(self.get_object().changelog, many=True, read_only=True).data
        return Response(sync.data)

    # noinspection PyUnusedLocal
    @action(detail=True, methods=['put'])
    def changelog(self, request, pk=None):
        # TODO: validate
        song = Song.objects.get(id=pk)
        if not self.request.user.can_sync(song):
            return HTTP_403_RESPONSE
        sync = song.sync_set.all().last()
        result = ChangelogEntry.objects.create(user=self.request.user,
                                               sync=sync,
                                               song=song,
                                               text=request.data['text'])
        return Response({'created': result.id})

    # noinspection PyUnusedLocal
    @action(detail=True, methods=['get'])
    def get_changelogs(self, request, pk=None):
        song = Song.objects.get(id=pk)
        if not self.request.user.can_sync(song):
            return HTTP_403_RESPONSE
        try:
            revision = int(request.query_params.get('since'))
        except (TypeError, ValueError):
            revision = None
        if revision is None:
            return HTTP_404_RESPONSE
        lookback = song.revision - revision
        result = ChangelogEntry.objects.filter(song=song).order_by('-id')[:lookback]
        return Response(ChangelogEntrySerializer(result, many=True).data)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ClientLogViewSet(viewsets.ModelViewSet):
    serializer_class = ClientLogSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrWriteOnly]
    queryset = ClientLog.objects.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, log_compressed=self.request.FILES.get('log_compressed').read())


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_backend_creds(request):
    return Response({'access_id': BACKEND_ACCESS_ID, 'secret_key': BACKEND_SECRET_KEY})


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def audio_sync(request):
    try:
        project = Project.objects.get(name=request.data['project'])
        song = Song.objects.get(name__iexact=request.data['song'], project=project)
    except (Song.DoesNotExist, Project.DoesNotExist):
        return HTTP_404_RESPONSE
    if not request.user.can_sync(song):
        return HTTP_403_RESPONSE
    AudioSync.objects.create(user=request.user, song=song)
    song.peaks = ""
    song.save()
    return Response({}, status=status.HTTP_204_NO_CONTENT)
