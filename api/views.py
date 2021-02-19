from django.contrib.auth.models import User, Group
from django.http import JsonResponse
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.decorators import api_view, action
from rest_framework.response import Response

from api.permissions import UserHasProjectAccess, AdminOrSelfOnly
from api.serializers import UserSerializer, GroupSerializer, ProjectSerializer, LockSerializer
from api.utils import get_tokens_for_user
from core.models import Lock


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


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated, UserHasProjectAccess]

    def get_queryset(self):
        return self.request.user.coreuser.projects.all()

    # noinspection PyUnusedLocal
    @action(detail=True, methods=['put', 'delete'])
    def lock(self, request, pk=None):
        project = self.get_object()
        if request.method == 'PUT':
            locked_by_user = project.is_locked_by_user(request.user)
            if locked_by_user and not request.data.get('force'):
                return Response({'status': 'locked', 'locked_by': 'self'})
            elif not locked_by_user and (lock := project.is_locked()):
                return Response({'status': 'locked', 'locked_by': lock.user.username, 'until': lock.end_time})
            else:
                return Response(LockSerializer(Lock.objects.create(project=project,
                                                                   user=request.user,
                                                                   reason=request.data.get('reason'))).data)
        elif request.method == 'DELETE':
            if project.is_locked_by_user(request.user) or request.data.get('force'):
                project.unlock()
                return Response({'status': 'unlocked'})
            elif lock := project.is_locked():
                return Response({'status': 'locked', 'locked_by': lock.user.username, 'until': lock.end_time},
                                status=408)
            else:
                return Response({'status': 'unlocked', 'locked_by': None}, status=412)


@api_view(['GET'])
def fetch_user_tokens(request):
    return JsonResponse(get_tokens_for_user(request.user))
