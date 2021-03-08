import hashlib
import hmac

from django.contrib.auth.models import User, Group
from django.http import JsonResponse
from rest_framework import permissions, status
from rest_framework import viewsets
from rest_framework.decorators import api_view, action, permission_classes, authentication_classes
from rest_framework.response import Response

from api.permissions import UserHasProjectAccess, AdminOrSelfOnly
from api.serializers import UserSerializer, GroupSerializer, ProjectSerializer, LockSerializer, ClientUpdateSerializer
from api.utils import get_tokens_for_user, update, awp_write_peaks, awp_read_peaks, CsrfExemptSessionAuthentication
from core.models import Song, Lock
from sync.models import ClientUpdate
from syncprojectsweb.settings import GOGS_SECRET


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


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAdminUser]


class ClientUpdateViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ClientUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = ClientUpdate.objects.all()


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated, UserHasProjectAccess]

    def get_queryset(self):
        return self.request.user.coreuser.projects.all()

    # noinspection PyUnusedLocal
    @action(detail=True, methods=['put', 'delete'])
    def lock(self, request, pk=None):
        project = self.get_object()
        if not self.request.user.coreuser.has_access_to(project):
            return Response({}, status=status.HTTP_403_FORBIDDEN)
        if 'song' in request.data:
            song = Song.objects.get(id=request.data['song'], project=project)
            obj = song
        else:
            obj = project

        if request.method == 'PUT':
            locked_by_user = obj.is_locked_by_user(request.user)
            if locked_by_user and not request.data.get('force'):
                return Response({'status': 'locked', 'locked_by': 'self'})
            elif not locked_by_user and (lock := obj.is_locked()):
                return Response({'status': 'locked',
                                 'locked_by': lock.user.username,
                                 'until': lock.end_time,
                                 'since': lock.start_time
                                 })
            else:
                return Response(LockSerializer(
                    Lock.objects.create(
                        object=obj,
                        user=request.user,
                        reason=request.data.get('reason'),
                        end_time=request.data.get('until'),
                    )).data)
        elif request.method == 'DELETE':
            if obj.is_locked_by_user(request.user) or request.data.get('force') and request.user.is_superuser:
                # success
                obj.unlock()
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
    if not request.user.coreuser.has_access_to(song):
        return Response({}, status=status.HTTP_403_FORBIDDEN)
    try:
        return Response({
                            'awp_write_peaks': awp_write_peaks,
                            'awp_read_peaks': awp_read_peaks,
                        }[request.data['action']](request.data, song), status=status.HTTP_200_OK)
    except KeyError:
        return Response({}, status=status.HTTP_400_BAD_REQUEST)
