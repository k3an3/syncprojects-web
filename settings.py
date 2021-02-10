from peewee import SqliteDatabase

db = SqliteDatabase('app.db')
SECRET_KEY = ""

try:
    from settings_local import *
except ImportError:
    pass