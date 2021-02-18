import datetime

import jwt

from syncprojectsweb.settings import PRIVATE_KEY


def get_signed_data(data):
    data["exp"] = datetime.datetime.utcnow()
    return jwt.encode(data, PRIVATE_KEY, algorithm="RS256")
