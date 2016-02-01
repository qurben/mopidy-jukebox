from __future__ import absolute_import, unicode_literals

import os

from mopidy import config, ext

__version__ = '0.0.1'


class Extension(ext.Extension):
    dist_name = 'Mopidy-Jukebox'
    ext_name = 'jukebox'
    version = __version__

    def get_config_schema(self):
        schema = super(Extension, self).get_config_schema()
        schema['db'] = config.String()
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
        # Get proper db file
        if config[self.ext_name]['db']:
            db_file = config[self.ext_name]['db']
        else:
            db_file = os.path.join(self.get_cache_dir(config), self.get_default_config()["db"])

        from .models import init
        init(db_file)

        from .web import IndexHandler, PlaylistHandler, TrackHandler, VoteHandler, SkipHandler, SearchHandler

        return [
            (r'/', IndexHandler, {'version': __version__, 'core': core}),
            (r'/playlist', PlaylistHandler, {'core': core}),
            (r'/track/(.+)', TrackHandler, {'core': core}),
            (r'/vote', VoteHandler, {'core': core}),
            (r'/skip/(.+)', SkipHandler, {'core': core}),
            (r'/search', SearchHandler, {'core': core}),
        ]
