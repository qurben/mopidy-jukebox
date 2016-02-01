"""
RequestHandlers for the Jukebox application

IndexHandler - Show version
TracklistHandler - Show current tracklist
SongHandler - Show track information
VoteHandler - Add and remove votes
SkipHandler - Add and remove skips
SearchHandler - Search the library
"""

from __future__ import absolute_import, unicode_literals

import json
from datetime import datetime

from mopidy.models import ModelJSONEncoder
from tornado import web

from .models import Vote, User
from .util import track_json


class IndexHandler(web.RequestHandler):
    def initialize(self, version, core):
        self.core = core
        self.version = version

    def get(self):
        self.write({'message': 'Welcome to the Jukebox API', 'version': self.version})
        self.set_header("Content-Type", "application/json")


class TracklistHandler(web.RequestHandler):
    def initialize(self, core):
        self.core = core

    def get(self):
        tracklist = self.core.tracklist.get_tl_tracks().get()

        self.write({
            'tracklist': [{'id': id, 'track': track_json(track)} for (id, track) in tracklist]
        })
        self.set_header("Content-Type", "application/json")


class TrackHandler(web.RequestHandler):
    def initialize(self, core):
        self.core = core

    def post(self):
        """
        Get information for a specific track
        :return:
        """
        track_uri = self.get_body_argument('track', '')
        if not track_uri:
            self.write({"error": "'track' key not found"})
            return self.set_status(400)

        track = self.core.library.lookup(track_uri).get()[0]

        self.write(track_json(track))


class VoteHandler(web.RequestHandler):
    def initialize(self, core):
        self.core = core

    def post(self):
        """
        Get the vote for a specific track
        :return:
        """
        user = User.current()
        track_uri = self.get_body_argument('track', '')
        vote = Vote.get(Vote.track_uri == track_uri)
        track = self.core.library.lookup(track_uri).get()[0]
        self.write({'track': track_json(track),
                    'user': user.name,
                    'timestamp': vote.timestamp.isoformat()})
        self.set_header("Content-Type", "application/json")

    def put(self):
        """
        Vote for a specific track
        :return:
        """
        track_uri = self.get_body_argument('track', '')
        if not track_uri:
            self.write({"error": "'track' key not found"})
            return self.set_status(400)

        my_vote = Vote(track_uri=track_uri, user=User.current(), timestamp=datetime.now())
        if my_vote.save() is 1:
            # Add this track to now playing TODO: remove
            self.core.tracklist.add(uris=[track_uri])
            self.set_status(204)
        else:
            self.set_status(500)

    def delete(self):
        """
        Delete the vote for a specific track
        :return:
        """
        track_uri = self.get_body_argument('track', '')
        if not track_uri:
            self.write({"error": "'track' key not found"})
            return self.set_status(400)

        q = Vote.delete().where(Vote.track_uri == track_uri and Vote.user == User.current())
        if q.execute() is 0:
            self.set_status(404, "No vote deleted")
        else:
            self.set_status(204, "Vote deleted")


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
