from __future__ import absolute_import, unicode_literals

from datetime import date

from tornado import web

from .models import Vote


class IndexHandler(web.RequestHandler):
    def initialize(self, core):
        self.core = core

    def get(self):
        for vote in Vote.select():
            print vote.song, vote.nick, vote.timestamp
        response = {'message': 'Welcome'}
        self.write(response)
        self.set_header("Content-Type", "application/json")


class VoteHandler(web.RequestHandler):
    def initialize(self, core):
        self.core = core


    def get(self, id):
        my_vote = Vote(song=id, nick="qurben", timestamp=date.today())
        my_vote.save()
        response = {'id': id,
                    'name': 'Crazy Game',
                    'release_date': date.today().isoformat()}
        self.write(response)
        self.set_header("Content-Type", "application/json")
