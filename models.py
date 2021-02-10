import datetime

from peewee import IntegrityError, Model, TextField, ManyToManyField, BooleanField, CharField, ForeignKeyField, \
    DateTimeField

from settings import db
from utils import gen_token, debug_enabled


def db_init() -> None:
    db.connect()
    try:
        db.create_tables(tables)
        print('Created tables.')
        if debug_enabled():
            User.create(username='admin', admin=True)
            User.create(username='user')
    except IntegrityError:
        pass
    db.close()


class BaseModel(Model):
    class Meta:
        database = db


class Project(BaseModel):
    name = CharField(unique=True)
    last_sync = DateTimeField(null=True)

    def is_locked(self) -> bool:
        return len(self.locks) > 0

    def is_locked_by_user(self, user) -> bool:
        return len(Lock.get(project=self, user=user))

    def lock(self, user):
        Lock.create(user=user, project=self)

    def unlock(self):
        for lock in self.locks:
            lock.delete_instance()

    def to_dict(self) -> dict:
        return {'name': self.name, 'locked': self.is_locked()}

    def __repr__(self):
        return f"<Project: {self.name}>"


class Song(BaseModel):
    name = CharField()
    project = ForeignKeyField(Project, backref='songs')
    updated = DateTimeField(null=True)
    created_at = DateTimeField(default=datetime.datetime.now)


class User(BaseModel):
    username = CharField(unique=True)
    admin = BooleanField(default=False)
    token = CharField(default=gen_token)
    projects = ManyToManyField(Project, backref='users')
    last_sync = DateTimeField(null=True)

    def get_token(self) -> bytes:
        from web import jws
        return jws.dumps({'username': self.username, 'token': self.token}).decode()

    def __repr__(self):
        return f"<User: {self.username}>"

    def to_dict(self) -> dict:
        return {'username': self.username, 'admin': self.admin, 'last_sync': self.last_sync.isoformat() if self.last_sync else 0,
                'token': self.get_token()}


class Lock(BaseModel):
    user = ForeignKeyField(User, backref='locks')
    project = ForeignKeyField(Project, backref='locks')
    start_time = DateTimeField(default=datetime.datetime.now)
    end_time = DateTimeField(null=True)
    reason = TextField()


tables = (Project, User, Lock, Song, User.projects.get_through_model())
