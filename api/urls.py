from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

from api.views import UserViewSet, GroupViewSet, ProjectViewSet, fetch_user_tokens, update_webhook, peaks

router = routers.DefaultRouter()
router.register(r'users', UserViewSet, 'user')
router.register(r'groups', GroupViewSet)
router.register(r'projects', ProjectViewSet, 'project')

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
    path('peaks/', peaks, name='peaks'),
    path('token/fetch/', fetch_user_tokens),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('webauth/', include('rest_framework.urls', namespace='rest_framework')),
    path('webhook/update/', update_webhook, name='update_webhook')
]
