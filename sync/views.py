from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from api.utils import get_tokens_for_user
from sync.utils import get_signed_data


@login_required
def send_sync_token(request):
    return render(request, 'sync/login.html', {'auth_data': get_signed_data(get_tokens_for_user(request.user))})
