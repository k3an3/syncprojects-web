from rest_framework import viewsets, permissions
from rest_framework.response import Response

from api.permissions import AdminOrSelfOnly
from users.api.serializers import UserSerializer
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
