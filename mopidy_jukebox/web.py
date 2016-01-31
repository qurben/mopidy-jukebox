from __future__ import absolute_import, unicode_literals

import json
from datetime import date

from mopidy.models import ModelJSONEncoder
from tornado import web

from .models import Vote, User


class IndexHandler(web.RequestHandler):
    def initialize(self, core):
        self.core = core

    def get(self):
        for vote in Vote.select():
            print vote.song, vote.nick, vote.timestamp
        response = {'message': 'Welcome'}
        self.write(response)
        self.set_header("Content-Type", "application/json")


class PlaylistHandler(web.RequestHandler):
    def initialize(self, core):
        self.core = core

    def get(self):
        self.write('hoeja')


class TrackHandler(web.RequestHandler):
    def initialize(self, core):
        self.core = core


class VoteHandler(web.RequestHandler):
    def initialize(self, core):
        self.core = core

    def get(self, id):
        my_user = User.current()
        my_vote = Vote(song=id, user=my_user, timestamp=date.today())
        my_vote.save()
        response = {'id': id,
                    'name': 'Crazy Game',
                    'release_date': date.today().isoformat()}
        self.write(response)
        self.set_header("Content-Type", "application/json")


class SkipHandler(web.RequestHandler):
    def initialize(self, core):
        self.core = core


class SearchHandler(web.RequestHandler):
    def initialize(self, core):
        self.core = core

    def error(self, code, message):
        self.write({
            'error': code,
            'message': message
        })

        self.set_status(code, message)

    def post(self):
        field = self.get_body_argument('field', '')
        values = self.get_body_argument('values', '')

        if not field:
            return self.error(400, 'Please provide a field')

        search = {field: [values]}

        search_result = self.core.library.search(search).get()[0]

        self.set_header("Content-Type", "application/json")
        self.write("""{
            "uri": "%s",
            "albums": %s,
            "artists": %s,
            "tracks": %s
        }""" % (search_result.uri,
                json.dumps(search_result.albums, cls=ModelJSONEncoder),
                json.dumps(search_result.artists, cls=ModelJSONEncoder),
                json.dumps(search_result.tracks, cls=ModelJSONEncoder)))
