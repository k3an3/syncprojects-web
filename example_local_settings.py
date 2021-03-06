from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DEBUG = False

ALLOWED_HOSTS = []
SECRET_KEY = ''

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

TIME_ZONE = 'EST'

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / "static"
]
STATIC_ROOT = BASE_DIR / "staticfiles"

INTERNAL_IPS = [
    '127.0.0.1',
]

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# Development key
PRIVATE_KEY = """-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEAsgFcJbSX6zfOhx/MImB2RY3vN1bXKN2dqz15B8os4yO9AdQI
KPcNagWXeA/gbY+3YXuS6bexBcZe+B4jltoSGHHyfRdmyAR3fDRvyBiehYkHK5u/
NEw6OWflE70LCfT6UJodmiPbFHG9zhgOkb7UbUzQg4Zoqg1tKD4ZkHzQCTMcJt1C
a4ai1LwajS0hUljr68GO7W3c51ADC0CD/K4pitIt0NfNqf7bwU439aaXh36Mv076
ydrnb46SH+0Wg/FrnlxpXVtUgPB0B7CGYrIHO14n0DFluLdcCjIvpgDZMYu4ZIof
iSx7FvPwB61KaQMZKgzeD/mPC1AaX7oQfiYjYQIDAQABAoIBAB3G0nZQPnWPkVHT
RN+fSUmbU5/rO/TPFbf2gY+HB3k7mjt7D55irXDF3K+t4DoTp3Z8KHhGTSuNIofY
6tUqR4qlTQ4V4xCkhqRVVTmgvKvT30oxNIv4EGlX8t8ZaYZR36mqDjehtd02payb
I5zH0lsyVVMbIdkIg/EOalJcPqS7C5ghOybMe7EbLNhjLYiTJN0MLui94wNFmdaq
3CSTzi0Ac4VCP4SP3PBZkEWw1/3BIf9so+k6H47nQofiD8q88P5ZbYRYZgsu7Hv1
ZSonV10T1+O6egzSU8gVKkAeNeOVAKYHPRfPIoeshTfuj8yMYMOFLyWmL6MRtZVA
0MRdBn0CgYEA1fZv86AusH+nMqnjwlSebmsBlz2MJzllDhy0KmP0ILZVsN3QOGyE
WpWkyUfU1fSbhrGvqPy/ty+XVtjNYD2ZGRkI/ZBNPuWTZIQXwtVGpa2cVvey/zAn
DJKG7MJsIklqzbMpsRMcG7+3DYlh9puqNsO0uy/gSPwp4UXjErtzLLsCgYEA1Ppl
bo0k75wejQ/FLm0fH747kRtNY1zH+VbFopUbw+zHwqjfEt/auTVpM6oUmExQ/ZZI
Tgt0C4qB26Cvfk50Qbl1nEiV0PbC20euIJ4mh4lWwEC/pi6bFanaJJKKjneZ8OdS
HUSH1GG+pnhSStUqbnCSx2+JrhVIWO36EHvtHJMCgYEAoKpZDpwt8yMoLgccnARm
o4t+uk7hO2MB20L6lwpPe3Dvj8xAWt5B1LOh9fMWg0MWtmIfAcopPClkfzZ1odsf
Z5VBBwaguqYxs7ztCsSUNDzVtQhzROSnre0pnAeyo1x18tiiafFrnfqsPmH3SfNC
MbVrtVQSGzwfRqXwCVTw+5kCgYBB5fA4kqeZFB9H2ldSlCULN1tK/L2nPvAJMFYa
hjR/HOZ6TrInLuiIYgRZHgkdTo/IxxU8QML5RzQC9ucWF8RVCcNgRf1FGPUV0EoK
gaS+TzpuZhpmmwkVXObIZidFCbCyH4EC2U+F4XCSJaygxvBIF8DywIpDOQaXrZqw
OwgUzQKBgH0F2WsoYiPM2Bnwqd4ryNXkMRWeh//sY+eM7IQE8QO6wslXX1fWFref
hqPpfD6ZAHBWEU+m+ecP6a8XcVjlOH5WH34wwTondDMJlWAAnWt154o9kTMmZI7B
x6sSqG4R9CuKVULL6A/TwzaUPmAaWWdR53LM4ugzqt9kbKNdlOuo
-----END RSA PRIVATE KEY-----"""

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
        },
    },
}
