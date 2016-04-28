from __future__ import absolute_import, unicode_literals

import os

from mopidy import config, ext

from tornado.web import StaticFileHandler

from .library import Tracklist
from .frontend import JukeboxFrontend
from .models import initialize_db
from .web import IndexHandler, TracklistHandler, TrackHandler, VoteHandler, SkipHandler, SearchHandler, \
    GoogleOAuth2LoginHandler, LoginHandler, LogoutHandler, UserHandler

__version__ = '0.0.1'


class Extension(ext.Extension):
    dist_name = 'Mopidy-Jukebox'
    ext_name = 'jukebox'
    version = __version__

    def get_config_schema(self):
        schema = super(Extension, self).get_config_schema()
        schema['db'] = config.String()
        schema['google_oauth'] = config.String()
        schema['google_oauth_secret'] = config.String()
        return schema

    def get_default_config(self):
        conf_file = os.path.join(os.path.dirname(__file__), 'ext.conf')
        return config.read(conf_file)

    def setup(self, registry):
        # Main Jukebox frontend
        registry.add('frontend', JukeboxFrontend)

        # HTTP api for frontend
        registry.add('http:app', {
            'name': 'jukebox-api',
            'factory': self.api_app,
        })

        # Static HTTP frontend
        registry.add('http:app', {
            'name': 'jukebox',
            'factory': self.static_app,
        })

    @staticmethod
    def static_app(conf, core):
        static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
        return [
            # If request contains a . it is a static file
            (r'/(.*\..*)', StaticFileHandler, dict(path=static_dir)),
            # Otherwise index.html will handle it
            (r'/.*()', StaticFileHandler, dict(path=os.path.join(static_dir, 'index.html'))),
        ]

    def api_app(self, conf, core):
        app_config = conf[self.ext_name]
        # Get proper db file and initialize it
        initialize_db(app_config['db'] or os.path.join(self.get_cache_dir(conf), self.get_default_config()["db"]))

        Tracklist.update_tracklist(core.tracklist)

        return [
            (r'/', IndexHandler, {'version': __version__, 'core': core}),
            (r'/tracklist', TracklistHandler, {'core': core}),
            (r'/track', TrackHandler, {'core': core}),
            (r'/vote', VoteHandler, {'core': core}),
            (r'/skip', SkipHandler, {'core': core}),
            (r'/search', SearchHandler, {'core': core}),
            (r'/user', UserHandler, {'core': core}),
            (r'/login', LoginHandler),
            (r'/logout', LogoutHandler),
            (r'/auth/google', GoogleOAuth2LoginHandler, {
                'google_oauth': app_config['google_oauth'],
                'google_oauth_secret': app_config['google_oauth_secret'],
            }),
        ]
