from peewee import SqliteDatabase, Model, CharField, DateField

db = SqliteDatabase(None)


class Vote(Model):
    song = CharField()
    nick = CharField()
    timestamp = DateField()


    class Meta:
        database = db
