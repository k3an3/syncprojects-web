from rest_framework import routers

from snippets.api import views

router = routers.DefaultRouter()
router.register(r'snippets', views.SnippetViewSet, 'snippets')

urlpatterns = [
]
