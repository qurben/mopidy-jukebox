"""
Models for the Jukebox application

User - All users
Vote - Votes on songs
"""

import logging

from peewee import SqliteDatabase, Model, CharField, DateField, ForeignKeyField

db = SqliteDatabase(None)
logger = logging.getLogger(__name__)


class User(Model):
    name = CharField()

    @staticmethod
    def current():
        return User.get(User.name == 'q')

    class Meta:
        database = db


class Vote(Model):
    # references a Mopidy track
    track_uri = CharField()
    user = ForeignKeyField(User, related_name='voter')
    timestamp = DateField()

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
        # create dummy user
        User(name="q").save()
