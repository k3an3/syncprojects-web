from functools import wraps

from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension
from flask_httpauth import HTTPTokenAuth
from flask_restful import Resource, Api, abort, reqparse
from itsdangerous import TimedJSONWebSignatureSerializer, BadSignature
from peewee import DoesNotExist, IntegrityError

from models import User, Project, db_init
from settings import SECRET_KEY
from utils import debug_enabled

app = Flask(__name__)
auth = HTTPTokenAuth(scheme='Bearer')
jws = TimedJSONWebSignatureSerializer(SECRET_KEY, 3600 * 24 * 365)
api = Api(app)
toolbar = DebugToolbarExtension(app)
project_parser = reqparse.RequestParser()
project_parser.add_argument('new_name', store_missing=False)
project_parser.add_argument('member', action='append')
lock_parser = reqparse.RequestParser()
lock_parser.add_argument('force', type=bool)
user_parser = reqparse.RequestParser()
user_parser.add_argument('admin', type=bool, default=False)
user_parser.add_argument('new_username', store_missing=False)


@auth.login_required
def admin_only(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if auth.current_user().admin:
            return func(*args, **kwargs)
        abort(403)

    return wrapper


@auth.login_required
def check_project(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            project = Project.get(name=kwargs.pop('project'))
            if auth.current_user().admin or project in auth.current_user().projects:
                return func(*args, project=project, **kwargs)
        except (KeyError, DoesNotExist):
            pass
        abort(404)

    return wrapper


class ProtectedResource(Resource):
    method_decorators = [auth.login_required]


class ProtectedAdminResource(Resource):
    method_decorators = [admin_only]


class ProtectedProjectResource(Resource):
    method_decorators = [check_project]


@auth.verify_token
def verify_token(token):
    try:
        user = User.get(**jws.loads(token))
    except (BadSignature, DoesNotExist):
        abort(403)
    return user


class ProjectList(ProtectedResource):
    @staticmethod
    def get():
        return {'projects': [project.name for project in auth.current_user().projects]}

    def post(self):
        pass


class ProjectLock(ProtectedProjectResource):
    @staticmethod
    def post(project):
        args = lock_parser.parse_args()
        if not args.force and project.is_locked() and not project.is_locked_by_user():
            abort(409)
        project.lock(auth.current_user())


class ProjectUnLock(ProtectedProjectResource):
    @staticmethod
    def post(project):
        args = lock_parser.parse_args()
        if not args.force and project.is_locked() and not project.is_locked_by_user():
            abort(409)
        project.unlock()


class Projects(Resource):
    method_decorators = {'get': [check_project],
                         'put': [admin_only],
                         'delete': [admin_only],
                         'post': [admin_only]}

    @staticmethod
    def get(project):
        return project.to_dict()

    @staticmethod
    def put(project):
        try:
            project = Project.create(name=project)
        except IntegrityError:
            abort(409)
        return project.to_dict()

    @staticmethod
    def delete(project):
        try:
            project = Project.get(name=project)
        except DoesNotExist:
            abort(404)
        project.delete_instance()
        return project.to_dict()

    @staticmethod
    def post(project):
        try:
            project = Project.get(name=project)
        except DoesNotExist:
            abort(404)
        args = project_parser.parse_args()
        for member in args['member']:
            print(member)
        if 'new_name' in args:
            project.name = args['new_name']
        project.save()
        print("fux")
        return project.to_dict()


class ProjectSongs(ProtectedProjectResource):
    @staticmethod
    def get(project):
        return {'songs': [song.name for song in project.songs]}


class UserList(ProtectedAdminResource):
    @staticmethod
    def get():
        return {'users': [user.username for user in User.select()]}


class UserSelf(ProtectedResource):
    @staticmethod
    def get():
        return auth.current_user().to_dict()


class Users(ProtectedAdminResource):
    @staticmethod
    def get(username):
        try:
            return User.get(username=username).to_dict()
        except DoesNotExist:
            abort(404)

    @staticmethod
    def put(username):
        args = user_parser.parse_args()
        try:
            user = User.create(username=username, admin=args['admin'])
        except IntegrityError:
            abort(409)
        return user.to_dict()

    @staticmethod
    def delete(username):
        try:
            user = User.get(username=username)
        except DoesNotExist:
            abort(404)
        user.delete_instance()
        return user.to_dict()

    @staticmethod
    def post(username):
        try:
            user = User.get(username=username)
        except DoesNotExist:
            abort(404)
        args = user_parser.parse_args()
        user.admin = args['admin']
        if 'new_username' in args:
            user.username = args['new_username']
        user.save()
        return user.to_dict()


api.add_resource(ProjectList, '/projects/')
api.add_resource(Projects, '/projects/<project>/')
api.add_resource(UserList, '/users/')
api.add_resource(Users, '/users/<username>/')
api.add_resource(UserSelf, '/users/self/')
api.add_resource(ProjectSongs, '/projects/<project>/songs/')
api.add_resource(ProjectLock, '/projects/<project>/lock/')

if __name__ == '__main__':
    db_init()
    app.run(debug=debug_enabled())
