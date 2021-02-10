from functools import wraps

from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension
from flask_httpauth import HTTPTokenAuth
from flask_restful import Resource, Api, abort
from itsdangerous import TimedJSONWebSignatureSerializer, BadSignature
from peewee import DoesNotExist

from models import User, Project
from settings import SECRET_KEY
from utils import debug_enabled

app = Flask(__name__)
auth = HTTPTokenAuth(scheme='Bearer')
jws = TimedJSONWebSignatureSerializer(SECRET_KEY, 3600 * 24 * 365)
api = Api(app)
toolbar = DebugToolbarExtension(app)


@auth.login_required
def admin_only(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if auth.current_user().admin:
            return func(*args, **kwargs)
        abort(403)

    return wrapper


class ProtectedResource(Resource):
    method_decorators = [auth.login_required]


class ProtectedAdminResource(Resource):
    method_decorators = [admin_only]


@auth.verify_token
def verify_token(token):
    try:
        user = User.get(**jws.loads(token))
    except (BadSignature, DoesNotExist):
        abort(403)
    return user


class ProjectList(ProtectedResource):
    def get(self):
        return {'projects': [{'name': project.name, 'locked': project.is_locked()} for project in auth.current_user().projects]}


class ProjectSongs(ProtectedResource):
    def get(self, project):
        try:
            project = Project.get(name=project)
            if project in auth.current_user().projects:
                return {'songs': [song.name for song in project.songs]}
        except DoesNotExist:
            pass
        abort(404)


class UserToken(ProtectedAdminResource):
    def get(self, username):
        return {'token': User.get(username=username).get_token()}


api.add_resource(ProjectList, '/projects/')
api.add_resource(UserToken, '/token/<username>/')
api.add_resource(ProjectSongs, '/projects/<project>/songs/')

if __name__ == '__main__':
    app.run(debug=debug_enabled())
