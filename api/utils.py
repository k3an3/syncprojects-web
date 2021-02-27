import subprocess
from os import mkdir
from os.path import join, exists, isdir

import sys
from django.contrib.auth.models import User
from rest_framework.authentication import SessionAuthentication
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


def awp_write_peaks(data):
    # TODO: use redis or something fast
    dest_file = join('peaks', f"{data['id']}.peaks")
    if not isdir('peaks'):
        mkdir('peaks')
    if exists(dest_file):
        # TODO: when to update based on song changes?
        return {'message': 'exists'}
    else:
        with open(dest_file, "w") as f:
            f.write(data['peaks'])
        return {'message': 'success'}


def awp_read_peaks(data):
    try:
        dest_file = join('peaks', f"{data['id']}.peaks")
        if not isdir('peaks'):
            mkdir('peaks')
        with open(dest_file) as f:
            peaks = [float(n) for n in f.read().split(',')]
        return peaks
    except (KeyError, FileNotFoundError):
        return ''


class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return
