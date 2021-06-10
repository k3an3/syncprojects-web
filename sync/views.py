from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import generic

from api.utils import get_tokens_for_user
from sync.models import SupportedClientTarget
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
