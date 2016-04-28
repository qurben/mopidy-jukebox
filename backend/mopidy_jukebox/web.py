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
import uuid
from datetime import datetime
from functools import wraps
from pprint import pprint

from mopidy.models import ModelJSONEncoder
from tornado import web, escape, gen, auth

from .library import Tracklist
from .models import Vote, User, Session
from .util import track_json


def authenticate(f):
    """
    Decorator for checking if a user is authenticated
    """

    @wraps(f)
    def wrapper(self):
        """
        :type self: RequestHandler
        """
        try:
            self.request.session = Session.get(Session.secret == self.get_cookie('session'))

            f(self)
        except Session.DoesNotExist:
            self.set_status(403)

    return wrapper


class LoginHandler(web.RequestHandler):
    def initialize(self):
        pass

    def get(self):
        cookie = self.get_cookie('session')
        if cookie:
            try:
                session = Session.get(Session.secret == cookie)
                self.set_status(200)
                self.write("Successfully logged in")
            except Session.DoesNotExist:
                self.redirect('/jukebox-api/auth/google')
        else:
            self.redirect('/jukebox-api/auth/google')


class LogoutHandler(web.RequestHandler):
    @authenticate
    def get(self):
        self.request.session.delete()
        self.clear_cookie('session')
        self.set_status(200)
        self.write("Successfully logged out")


class GoogleOAuth2LoginHandler(web.RequestHandler,
                               auth.GoogleOAuth2Mixin):
    def initialize(self, google_oauth, google_oauth_secret):
        self.settings[self._OAUTH_SETTINGS_KEY] = {
            'key': google_oauth,
            'secret': google_oauth_secret,
        }

    @gen.coroutine
    def get(self):
        # own url without GET variables
        redirect_uri = self.request.protocol + "://" + self.request.host + self.request.uri.split('?')[0]
        if self.get_argument('code', False):
            try:
                access = yield self.get_authenticated_user(
                    redirect_uri=redirect_uri,
                    code=self.get_argument('code'))
                google_user = yield self.oauth2_request(
                    "https://www.googleapis.com/oauth2/v1/userinfo",
                    access_token=access["access_token"])

                try:
                    user = User.get(uid=google_user['id'])
                except User.DoesNotExist:
                    print 'user does not exist'
                    user = User.create(uid=google_user['id'], name=google_user['name'], email=google_user['email'],
                                       picture=google_user['picture'])
                    user.save()

                # a user can have 1 session
                Session.delete().where(Session.user == user).execute()

                session = Session(user=user, secret=uuid.uuid1())
                session.save()

                self.set_cookie('session', str(session.secret))

                self.set_status(200)
                self.write("Successfully logged in")
            except auth.AuthError:
                self.set_status(400, "Bad Request")
                self.write("400: Bad Request")
        else:
            yield self.authorize_redirect(
                redirect_uri=redirect_uri,
                client_id=self.settings[self._OAUTH_SETTINGS_KEY]['key'],
                scope=['profile', 'email'],
                response_type='code',
                extra_params={'approval_prompt': 'auto'})


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

    @authenticate
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
        try:
            track_uri = self.get_body_argument('track', '')

            track = self.core.library.lookup(track_uri).get()[0]

            self.write(track_json(track))
        except web.MissingArgumentError:
            self.write({"error": "'track' key not found"})
            self.set_status(400)


class UserHandler(web.RequestHandler):
    def initialize(self, core):
        self.core = core

    @authenticate
    def get(self):
        """
        Get information about the active user
        :return:
        """
        user = self.request.session.user

        self.set_header("Content-Type", "application/json")
        self.write({
            'name': user.name,
            'picture': user.picture,
            'email': user.email,
            'uid': user.uid,
        })


class VoteHandler(web.RequestHandler):
    def initialize(self, core):
        self.core = core

    @authenticate
    def post(self):
        """
        Get the vote for a specific track
        :return:
        """
        user = self.request.session.user

        try:
            track_uri = self.get_body_argument('track')

            vote = Vote.get(Vote.track_uri == track_uri)
            track = self.core.library.lookup(track_uri).get()[0]
            self.write({'track': track_json(track),
                        'user': user.name,
                        'timestamp': vote.timestamp.isoformat()})
            self.set_header("Content-Type", "application/json")
        except web.MissingArgumentError:
            self.set_status(400)
            self.write({"error": "'track' key not found"})

    @authenticate
    def put(self):
        """
        Vote for a specific track
        :return:
        """
        try:
            track_uri = self.get_body_argument('track')
            active_user = self.request.session.user

            if Vote.select().where(Vote.track_uri == track_uri, Vote.user == active_user):
                return self.set_status(409, 'Vote already exists')

            my_vote = Vote(track_uri=track_uri, user=active_user, timestamp=datetime.now())
            if my_vote.save() is 1:
                # Add this track to now playing TODO: remove
                Tracklist.update_tracklist(self.core.tracklist)
                self.set_status(201)
            else:
                self.set_status(500)
        except web.MissingArgumentError:
            self.set_status(400)
            self.write({"error": "'track' key not found"})

    @authenticate
    def delete(self):
        """
        Delete the vote for a specific track
        :return:
        """
        data = escape.json_decode(self.request.body)
        track_uri = data['track']
        if not track_uri:
            self.write({"error": "'track' key not found"})
            return self.set_status(400)

        active_user = self.request.session.user

        q = Vote.delete().where(Vote.track_uri == track_uri and Vote.user == active_user)
        if q.execute() is 0:
            self.set_status(404, "No vote deleted")
        else:
            Tracklist.update_tracklist(self.core.tracklist)
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
