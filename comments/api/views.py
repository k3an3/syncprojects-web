from django.http import JsonResponse
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from api.views import HTTP_403_RESPONSE
from comments.api.serializers import CommentSerializer
from comments.models import Comment, CommentLike
from core.models import Song, Project


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

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
        serializer.save(user=self.request.user)

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
