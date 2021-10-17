from django.http import JsonResponse
from rest_framework import permissions
from rest_framework.decorators import permission_classes, api_view, authentication_classes

from api.utils import CsrfExemptSessionAuthentication
from api.views import HTTP_404_RESPONSE, HTTP_403_RESPONSE
from todo.models import Todo


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
@authentication_classes([CsrfExemptSessionAuthentication])
def handle_check(request):
    try:
        todo = Todo.objects.get(id=request.data['id'])
    except Todo.DoesNotExist:
        return HTTP_404_RESPONSE
    if not request.user.can_sync(todo.project):
        return HTTP_403_RESPONSE
    todo.done = not todo.done
    todo.save()
    return JsonResponse({'checked': todo.done})
