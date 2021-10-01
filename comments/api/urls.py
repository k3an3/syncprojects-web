from rest_framework import routers

from comments.api import views

router = routers.DefaultRouter()
router.register(r'comments', views.CommentViewSet, 'comment')

urlpatterns = [
]
