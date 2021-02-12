from django.contrib.auth.models import User, Group
from django.http import JsonResponse
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.decorators import api_view, action

from api.serializers import UserSerializer, GroupSerializer, ProjectSerializer, SongSerializer
from api.utils import get_tokens_for_user


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]


class ProjectViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.request.user.coreuser.projects.all()


@api_view(['GET'])
def fetch_user_tokens(request):
    return JsonResponse(get_tokens_for_user(request.user))
