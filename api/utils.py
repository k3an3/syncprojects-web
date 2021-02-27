import subprocess

import sys
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken

from syncprojectsweb.settings import SYSTEMD_UNIT


def get_tokens_for_user(user: User):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


def update():
    subprocess.run(["git", "pull"])
    try:
        subprocess.run([sys.executable, "./manage.py", "migrate"])
        subprocess.run([sys.executable, "./manage.py", "collectstatic", "--noinput"])
    except TypeError:
        pass
    subprocess.run(["sudo", "systemctl", "restart", SYSTEMD_UNIT])
