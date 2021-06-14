from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render
from django.views import generic

from api.utils import get_tokens_for_user
from sync.models import SupportedClientTarget, ClientLog
from sync.utils import get_signed_data


@login_required
def send_sync_token(request):
    return render(request, 'sync/login.html',
                  {'auth_data': get_signed_data(get_tokens_for_user(request.user))})


@login_required
def authorization_success(request):
    return render(request, 'sync/authz_complete.html')


class DownloadIndexView(LoginRequiredMixin, generic.ListView):
    model = SupportedClientTarget
    template_name = 'sync/download.html'
    context_object_name = 'supported_targets'


class UserLogIndexView(LoginRequiredMixin, UserPassesTestMixin, generic.ListView):
    model = ClientLog

    def test_func(self):
        return self.request.user.is_superuser

    def get_queryset(self):
        return ClientLog.objects.filter(user_id=self.kwargs['user'])

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['log_user'] = get_user_model().objects.get(id=self.kwargs['user'])
        return context


class UserLogDetailView(LoginRequiredMixin, UserPassesTestMixin, generic.DetailView):
    model = ClientLog

    def test_func(self):
        return self.request.user.is_superuser

    def get_queryset(self):
        return ClientLog.objects.filter(user_id=self.kwargs['user'])

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['log_user'] = get_user_model().objects.get(id=self.kwargs['user'])
        return context
