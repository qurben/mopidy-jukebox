from __future__ import absolute_import, unicode_literals

import os

from mopidy import config, ext

from .library import Tracklist

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
        from .frontend import JukeboxFrontend
        registry.add('frontend', JukeboxFrontend)

        # HTTP api for frontend
        registry.add('http:app', {
            'name': 'jukebox-api',
            'factory': self.webapp,
        })
        directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
        registry.add('http:static', dict(name=self.ext_name, path=directory))

    def webapp(self, config, core):
        app_config = config[self.ext_name]
        # Get proper db file
        if app_config['db']:
            db_file = app_config['db']
        else:
            db_file = os.path.join(self.get_cache_dir(config), self.get_default_config()["db"])

        from .models import init
        init(db_file)

        Tracklist.update_tracklist(core.tracklist)

        from .web import IndexHandler, TracklistHandler, TrackHandler, VoteHandler, SkipHandler, SearchHandler, GoogleOAuth2LoginHandler, LoginHandler, UserHandler

        return [
            (r'/', IndexHandler, {'version': __version__, 'core': core}),
            (r'/tracklist', TracklistHandler, {'core': core}),
            (r'/track', TrackHandler, {'core': core}),
            (r'/vote', VoteHandler, {'core': core}),
            (r'/skip', SkipHandler, {'core': core}),
            (r'/search', SearchHandler, {'core': core}),
            (r'/user', UserHandler, {'core': core}),
            (r'/auth', LoginHandler),
            (r'/auth/google', GoogleOAuth2LoginHandler, {
                'google_oauth': app_config['google_oauth'],
                'google_oauth_secret': app_config['google_oauth_secret'],
            }),
        ]
