import hashlib
import hmac
from django.http import JsonResponse
from rest_framework import permissions, status, mixins
from rest_framework import viewsets
from rest_framework.decorators import api_view, action, permission_classes, authentication_classes
from rest_framework.response import Response

from api.permissions import UserHasProjectAccess
from api.serializers import ProjectSerializer, LockSerializer, SongSerializer, AlbumSerializer
from api.utils import update, awp_write_peaks, awp_read_peaks, CsrfExemptSessionAuthentication, get_tokens_for_user
from core.models import Song, Lock, Album
from sync.models import ChangelogEntry
from sync.utils import get_signed_data
from syncprojectsweb.settings import GOGS_SECRET

HTTP_404_RESPONSE = Response({}, status=status.HTTP_404_NOT_FOUND)
HTTP_403_RESPONSE = Response({}, status=status.HTTP_403_FORBIDDEN)


class SongViewSet(viewsets.ModelViewSet):
    serializer_class = SongSerializer
    permission_classes = [permissions.IsAuthenticated, UserHasProjectAccess]

    def get_queryset(self):
        songs = self.request.user.collab_songs.all()
        for project in self.request.user.projects.all():
            songs |= (project.songs())
        return songs

    # noinspection PyUnusedLocal
    @action(detail=True, methods=['get'])
    def url(self, request, pk=None):
        return JsonResponse({'url': self.get_object().get_signed_url()})

    # noinspection PyUnusedLocal
    @action(detail=True, methods=['put'])
    def changelog(self, request, pk=None):
        song = Song.objects.get(id=pk)
        if not self.request.user.can_sync(song):
            return Response({}, status=status.HTTP_403_FORBIDDEN)
        sync = song.sync_set.all().last()
        result = ChangelogEntry.objects.create(user=self.request.user,
                                               sync=sync,
                                               song=song,
                                               text=request.data['text'])
        return Response({'created': result.id})


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated, UserHasProjectAccess]

    def get_queryset(self):
        return (self.request.user.projects.all() | self.request.user.subscribed_projects.all()).distinct()

    # noinspection PyUnusedLocal
    @action(detail=True, methods=['put', 'delete'])
    def lock(self, request, pk=None):
        project = self.get_object()
        transient_lock = None
        if 'song' in request.data:
            song = Song.objects.get(id=request.data['song'], project=project)
            if not self.request.user.can_sync(song):
                return HTTP_403_RESPONSE
            if not song.project.is_locked_by_user(request.user) and (lock := song.project.is_locked()):
                return Response({'status': 'locked',
                                 'locked_by': lock.user.username,
                                 'until': lock.end_time,
                                 'since': lock.start_time
                                 })
            transient_lock = Lock.objects.create(object=song.project, user=request.user,
                                                 reason=f"transient {song.name=}")
            obj = song
        else:
            if not self.request.user.has_member_access(project):
                # Check if the user has any songs from this project. If so, just pretend they got the lock and let
                # them continue
                if self.request.user.collab_songs.filter(project=project).count():
                    if lock := project.is_locked():
                        return Response({'status': 'locked',
                                         'locked_by': lock.user.username,
                                         'until': lock.end_time,
                                         'since': lock.start_time
                                         })
                    return Response({'id': 1})
                else:
                    return HTTP_403_RESPONSE
            obj = project

        if request.method == 'PUT':
            locked_by_user = obj.is_locked_by_user(request.user)
            if locked_by_user and not request.data.get('force'):
                if transient_lock:
                    transient_lock.delete()
                return Response({'status': 'locked', 'locked_by': 'self'})
            elif not locked_by_user and (lock := obj.is_locked()):
                if transient_lock:
                    transient_lock.delete()
                return Response({'status': 'locked',
                                 'locked_by': lock.user.username,
                                 'until': lock.end_time,
                                 'since': lock.start_time
                                 })
            else:
                resp = Response(LockSerializer(
                    Lock.objects.create(
                        object=obj,
                        user=request.user,
                        reason=request.data.get('reason'),
                        end_time=request.data.get('until'),
                    )).data)
                if 'song' in request.data:
                    song.project.unlock()
                return resp
        elif request.method == 'DELETE':
            if obj.is_locked_by_user(request.user) or request.data.get('force') and request.user.is_superuser:
                # success
                obj.unlock()
                if 'song' in request.data:
                    song.project.unlock()
                return Response({'result': 'success'})
            elif lock := obj.is_locked():
                # locked by someone else
                return Response({'status': 'locked',
                                 'locked_by': lock.user.username,
                                 'since': lock.start_time,
                                 'until': lock.end_time})
            else:
                # already unlocked
                return Response({'status': 'unlocked', 'locked_by': None})


class AlbumViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = AlbumSerializer
    permission_classes = [permissions.IsAuthenticated, UserHasProjectAccess]
    queryset = Album.objects.all()


@api_view(['POST'])
def update_webhook(request):
    if request.headers.get('X-Gogs-Signature'):
        secret = bytes(GOGS_SECRET.encode())
        mac = hmac.new(secret, msg=request.body, digestmod=hashlib.sha256)
        if hmac.compare_digest(mac.hexdigest(), request.headers['X-Gogs-Signature']):
            if request.data.get("ref") in {"refs/heads/master", "refs/heads/main"}:
                update()
            return Response({}, status=status.HTTP_204_NO_CONTENT)
    return HTTP_403_RESPONSE


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
@authentication_classes([CsrfExemptSessionAuthentication])
def peaks(request):
    try:
        song = Song.objects.get(name=request.data['id'])
    except Song.DoesNotExist:
        return HTTP_404_RESPONSE
    if not request.user.can_sync(song) and not request.user.is_superuser:
        return HTTP_403_RESPONSE
    try:
        return Response({
                            'awp_write_peaks': awp_write_peaks,
                            'awp_read_peaks': awp_read_peaks,
                        }[request.data['action']](request.data, song), status=status.HTTP_200_OK)
    except KeyError:
        return Response({}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
# @authentication_classes([CsrfExemptSessionAuthentication])
def sign_data(request):
    data = request.data.copy()
    return Response({'data': get_signed_data(data, request.user)})


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def fetch_user_tokens(request):
    return JsonResponse(get_tokens_for_user(request.user))
