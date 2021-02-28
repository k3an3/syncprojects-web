import datetime
import subprocess
from json import JSONDecodeError

import requests
import sys
from django.contrib.auth.models import User
from pytz import UTC
from requests import HTTPError
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

from syncprojectsweb.settings import SYSTEMD_UNIT, SEAFILE_API_URL, SEAFILE_TOKEN


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


def awp_write_peaks(data, song):
    # TODO: use redis or something fast
    if song.peaks:
        return {'message': 'exists'}
    else:
        song.peaks = data['peaks']
        song.save()
        return {'message': 'success'}


def awp_read_peaks(_, song):
    try:
        if SEAFILE_API_URL and SEAFILE_TOKEN:
            if check_song_updated(song):
                song.clear_peaks()
                return ''
        peaks = [float(n) for n in song.peaks.split(',')]
        return peaks
    except (ValueError, AttributeError, JSONDecodeError, HTTPError):
        return ''


def check_song_updated(song):
    r = requests.get(f"{SEAFILE_API_URL}repos/{song.project.seafile_uuid}/file/detail/",
                     params={'p': f"{song.name}.mp3"},
                     headers={'Authorization': f'Token {SEAFILE_TOKEN}'}).json()
    mtime = datetime.datetime.utcfromtimestamp(r['mtime'])
    old_mtime = song.last_mtime
    song.last_mtime = mtime
    song.save()
    return not old_mtime or mtime.replace(tzinfo=UTC) > old_mtime


class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return
