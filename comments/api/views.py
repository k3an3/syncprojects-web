from django.core.exceptions import ValidationError
from django.http import JsonResponse
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from api.permissions import UserHasProjectMemberAccess
from api.views import HTTP_403_RESPONSE
from comments.api.serializers import CommentSerializer, TagSerializer
from comments.models import Comment, CommentLike, Tag
from core.models import Song, Project


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated, UserHasProjectMemberAccess]

    def get_queryset(self):
        project = self.request.query_params.get('project')
        song = self.request.query_params.get('song')
        for name, param in (('song', song), ('project', project)):
            if not param:
                continue
            _class = {'song': Song, 'project': Project}[name]
            try:
                obj = _class.objects.get(id=param)
            except _class.DoesNotExist:
                return Comment.objects.none()
            if not self.request.user.can_sync(obj):
                return Comment.objects.none()
            return Comment.objects.filter(**{name: obj})
        return self.request.user.comment_set.all()

    def perform_create(self, serializer):
        if self.request.data.get('song'):
            obj = Song.objects.get(id=self.request.data['song'])
        else:
            obj = Project.objects.get(id=self.request.data['project'])
        if not self.request.user.can_sync(obj) and not self.request.user.has_subscriber_access(obj):
            raise ValidationError("Access denied")
        serializer.save(user=self.request.user, internal=self.request.user.can_sync(obj))

    # noinspection PyUnusedLocal
    @action(detail=True, methods=['post'])
    def unresolve(self, request, pk=None):
        comment = Comment.objects.get(id=pk)
        if not request.user.has_member_access(comment.song):
            return HTTP_403_RESPONSE
        comment.requires_resolution = True
        comment.resolved = False
        comment.save()
        return Response({}, status=status.HTTP_204_NO_CONTENT)

    # noinspection PyUnusedLocal
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        comment = Comment.objects.get(id=pk)
        if not request.user.has_member_access(comment.song):
            return HTTP_403_RESPONSE
        comment.requires_resolution = True
        comment.resolved = True
        comment.save()
        return Response({}, status=status.HTTP_204_NO_CONTENT)

    # noinspection PyUnusedLocal
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        comment = Comment.objects.get(id=pk)
        if comment.song:
            obj = comment.song
        else:
            obj = comment.project
        if not request.user.has_subscriber_access(obj) and not request.user.has_member_access(obj):
            return HTTP_403_RESPONSE
        elif request.user == comment.user:
            return Response({}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        like, created = CommentLike.objects.get_or_create(user=request.user, comment=comment)
        if not created:
            like.delete()
        return JsonResponse({'likes': comment.likes, 'liked': created})


class TagViewSet(viewsets.ModelViewSet):
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticated, UserHasProjectMemberAccess]

    def get_queryset(self):
        project = self.request.query_params.get('project')
        try:
            project = Project.objects.get(id=project)
        except Project.DoesNotExist:
            return Tag.objects.none()
        if not self.request.user.can_sync(project):
            return Tag.objects.none()
        return Tag.objects.filter(project=project)
