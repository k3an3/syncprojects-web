from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic


class UserDetailView(LoginRequiredMixin, generic.DetailView):
    model = get_user_model()

    def get_context_object_name(self, obj):
        return 'profile_user'

    def get_object(self, queryset=None):
        return get_user_model().objects.get(id=self.kwargs['pk']) if 'pk' in self.kwargs else self.request.user
