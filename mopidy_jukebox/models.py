"""
Models for the Jukebox application

User - All users
Vote - Votes on songs
"""

import datetime
import logging

from peewee import SqliteDatabase, Model, CharField, DateTimeField, ForeignKeyField, UUIDField

db = SqliteDatabase(None)
logger = logging.getLogger(__name__)


class User(Model):
    uid = CharField()
    name = CharField()
    picture = CharField()
    email = CharField()

    class Meta:
        database = db


class Vote(Model):
    # references a Mopidy track
    track_uri = CharField()
    user = ForeignKeyField(User, related_name='voter')
    timestamp = DateTimeField()

    class Meta:
        database = db


class Session(Model):
    user = ForeignKeyField(User)
    secret = UUIDField()
    expires = DateTimeField(default=datetime.datetime.now() + datetime.timedelta(days=30))  # expires after 30 days

    class Meta:
        database = db


def init(db_file):
    # Create db
    db.init(db_file)

    # Create tables
    if not Vote.table_exists():
        Vote.create_table()
    if not User.table_exists():
        User.create_table()
    if not Session.table_exists():
        Session.create_table()
