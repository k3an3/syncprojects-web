import datetime

import jwt

from syncprojectsweb.settings import PRIVATE_KEY


def get_signed_data(data, user):
    data["exp"] = datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
    data["user"] = user.username
    return jwt.encode(data, PRIVATE_KEY, algorithm="RS256")
