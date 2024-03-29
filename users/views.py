from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.views import generic, View
from rest_framework.authtoken.models import Token


class UserDetailView(LoginRequiredMixin, generic.DetailView):
    model = get_user_model()

    def get_context_object_name(self, obj):
        return 'profile_user'

    def get_object(self, queryset=None):
        return get_user_model().objects.get(id=self.kwargs['pk']) if 'pk' in self.kwargs else self.request.user


class UserUpdateView(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
    template_name_suffix = '_update_form'
    model = get_user_model()
    fields = ['email', 'profile_picture', 'bio',
              'instruments', 'genres_musical_taste', 'links', 'open_to_collaboration',
              'private']

    def get_object(self, queryset=None):
        return self.request.user

    def test_func(self):
        return self.get_object() == self.request.user

    def get_success_url(self):
        return reverse('users:user-profile')


class UserTokenView(LoginRequiredMixin, View):
    def post(self, *args, **kwargs):
        token, created = Token.objects.get_or_create(user=self.request.user)
        if not created:
            token.delete()
            Token.objects.create(user=self.request.user)
        return redirect('users:user-profile')
