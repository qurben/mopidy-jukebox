from __future__ import unicode_literals

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
        registry.add('http:app', {
            'name': 'jukebox-api',
            'factory': self.webapp,
        })
        directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
        registry.add('http:static', dict(name=self.ext_name, path=directory))

    def webapp(self, config, core):
        from .web import IndexHandler, VoteHandler
        if config[self.ext_name]['db']:
            db = config[self.ext_name]['db']
        else:
            db = self.get_default_config()["db"]

        db_file = os.path.join(self.get_cache_dir(config), db)

        from models import vote
        vote.db.init(db_file)
        if not vote.Vote.table_exists():
            vote.Vote.create_table()
        return [
            (r'/(?:index.html)?', IndexHandler, {'core': core}),
            (r'/vote/(.+)', VoteHandler, {'core': core})
        ]
