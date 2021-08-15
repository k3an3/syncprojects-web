import hashlib
import hmac

from django.http import JsonResponse
from rest_framework import permissions, status
from rest_framework import viewsets
from rest_framework.decorators import api_view, action, permission_classes, authentication_classes
from rest_framework.response import Response

from api.permissions import AdminOrSelfOnly, UserHasProjectAccess, CreateOrReadOnly, \
    IsAdminOrWriteOnly
from api.serializers import UserSerializer, ProjectSerializer, LockSerializer, ClientUpdateSerializer, SyncSerializer, \
    ChangelogEntrySerializer, SongSerializer, ClientLogSerializer, CommentSerializer
from api.utils import get_tokens_for_user, update, awp_write_peaks, awp_read_peaks, CsrfExemptSessionAuthentication
from core.models import Song, Lock, Comment, Project
from sync.models import ClientUpdate, ChangelogEntry, Sync, SupportedClientTarget, ClientLog, AudioSync
from sync.utils import get_signed_data
from syncprojectsweb.settings import GOGS_SECRET, BACKEND_ACCESS_ID, BACKEND_SECRET_KEY
from users.models import User


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, AdminOrSelfOnly]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return User.objects.all().order_by('-date_joined')
        return User.objects.filter(pk=self.request.user.pk)

    def retrieve(self, request, pk=None):
        if pk == "self" or pk == request.user.pk:
            user = request.user
        elif request.user.is_superuser:
            user = User.objects.get(pk=pk)
        else:
            return super().retrieve(request, pk)
        return Response(UserSerializer(user, context={'request': request}).data)


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
            return ClientUpdate.objects.filter(target=target)
        else:
            return ClientUpdate.objects.filter(target__isnull=True)


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
            return Response({}, status=status.HTTP_403_FORBIDDEN)
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
            return Response({}, status=status.HTTP_403_FORBIDDEN)
        try:
            revision = int(request.query_params.get('since'))
        except (TypeError, ValueError):
            revision = None
        if revision is None:
            return Response({}, status=status.HTTP_404_NOT_FOUND)
        lookback = song.revision - revision
        result = ChangelogEntry.objects.filter(song=song).order_by('-id')[:lookback]
        return Response(ChangelogEntrySerializer(result, many=True).data)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


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



class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.request.user.comment_set.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    # noinspection PyUnusedLocal
    @action(detail=True, methods=['post'])
    def unresolve(self, request, pk=None):
        comment = Comment.objects.get(id=pk)
        if not self.request.user.has_member_access(comment.song):
            return Response({}, status=status.HTTP_403_FORBIDDEN)
        comment.requires_resolution = True
        comment.resolved = False
        comment.save()
        return Response({}, status=status.HTTP_204_NO_CONTENT)

    # noinspection PyUnusedLocal
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        comment = Comment.objects.get(id=pk)
        if not self.request.user.has_member_access(comment.song):
            return Response({}, status=status.HTTP_403_FORBIDDEN)
        comment.requires_resolution = True
        comment.resolved = True
        comment.save()
        return Response({}, status=status.HTTP_204_NO_CONTENT)


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
                return Response({}, status=status.HTTP_403_FORBIDDEN)
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
                return Response({}, status=status.HTTP_403_FORBIDDEN)
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


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def fetch_user_tokens(request):
    return JsonResponse(get_tokens_for_user(request.user))


@api_view(['POST'])
def update_webhook(request):
    if request.headers.get('X-Gogs-Signature'):
        secret = bytes(GOGS_SECRET.encode())
        mac = hmac.new(secret, msg=request.body, digestmod=hashlib.sha256)
        if hmac.compare_digest(mac.hexdigest(), request.headers['X-Gogs-Signature']):
            if request.data.get("ref") == "refs/heads/master":
                update()
            return Response({}, status=status.HTTP_204_NO_CONTENT)
    return Response({}, status=status.HTTP_403_FORBIDDEN)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
@authentication_classes([CsrfExemptSessionAuthentication])
def peaks(request):
    # TODO: authz, CSRF
    try:
        song = Song.objects.get(name=request.data['id'])
    except Song.DoesNotExist:
        return Response({}, status=status.HTTP_404_NOT_FOUND)
    if not request.user.has_member_access(song) and not request.user.is_superuser:
        return Response({}, status=status.HTTP_403_FORBIDDEN)
    try:
        return Response({
                            'awp_write_peaks': awp_write_peaks,
                            'awp_read_peaks': awp_read_peaks,
                        }[request.data['action']](request.data, song), status=status.HTTP_200_OK)
    except KeyError:
        return Response({}, status=status.HTTP_400_BAD_REQUEST)


class ClientLogViewSet(viewsets.ModelViewSet):
    serializer_class = ClientLogSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrWriteOnly]
    queryset = ClientLog.objects.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, log_compressed=self.request.FILES.get('log_compressed').read())


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
# @authentication_classes([CsrfExemptSessionAuthentication])
def sign_data(request):
    data = request.data.copy()
    return Response({'data': get_signed_data(data, request.user)})


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_backend_creds(request):
    return Response({'access_id': BACKEND_ACCESS_ID, 'secret_key': BACKEND_SECRET_KEY})


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def audio_sync(self, request):
    try:
        project = Project.objects.get(name=request.data['project'])
        song = Song.objects.get(name__iexact=request.data['song'], project=project)
    except (Song.DoesNotExist, Project.DoesNotExist):
        return Response({}, status=status.HTTP_404_NOT_FOUND)
    if not self.request.user.can_sync(song):
        return Response({}, status=status.HTTP_403_FORBIDDEN)
    AudioSync.objects.create(user=request.user, song=song)
    return Response({}, status=status.HTTP_204_NO_CONTENT)
