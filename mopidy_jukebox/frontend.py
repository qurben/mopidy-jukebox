import pykka

from mopidy import core

from models import Vote


class JukeboxFrontend(pykka.ThreadingActor, core.CoreListener):
    def __init__(self, config, core):
        super(JukeboxFrontend, self).__init__()
        self.core = core
        core.tracklist.set_consume(True)

    def track_playback_ended(self, tl_track, time_position):
        # Remove old votes
        Vote.delete().where(Vote.track_uri == tl_track.track.uri).execute()

    def track_playback_started(self, tl_track):
        pass
