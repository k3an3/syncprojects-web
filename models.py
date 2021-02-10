import datetime

from peewee import IntegrityError, Model, TextField, ManyToManyField, BooleanField, CharField, ForeignKeyField, \
    DateTimeField

from settings import db
from utils import gen_token, debug_enabled


def db_init() -> None:
    db.connect()
    try:
        print('Creating tables...')
        db.create_tables(tables)
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
    name = TextField(unique=True)

    def is_locked(self) -> bool:
        return len(self.locks) > 0

    def lock(self, user):
        Lock.create(user=user, project=self)

    def unlock(self):
        for lock in self.locks:
            lock.delete_instance()

    def as_dict(self):
        return {'name': self.name, 'locked': self.is_locked()}

    def __repr__(self):
        return f"<Project: {self.name}>"


class Song(BaseModel):
    name = TextField()
    project = ForeignKeyField(Project, backref='songs')


class User(BaseModel):
    username = CharField(unique=True)
    admin = BooleanField(default=False)
    token = CharField(default=gen_token)
    projects = ManyToManyField(Project, backref='users')

    def get_token(self) -> bytes:
        from web import jws
        return jws.dumps({'username': self.username, 'token': self.token})

    def __repr__(self):
        return f"<User: {self.username}>"


class Lock(BaseModel):
    user = ForeignKeyField(User, backref='locks')
    project = ForeignKeyField(Project, backref='locks')
    start_time = DateTimeField(default=datetime.datetime.now)


tables = (Project, User, Lock, Song, User.projects.get_through_model())
