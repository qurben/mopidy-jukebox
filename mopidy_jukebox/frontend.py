import pykka

from mopidy import core


class JukeboxFrontend(pykka.ThreadingActor, core.CoreListener):
    def __init__(self, config, core):
        super(JukeboxFrontend, self).__init__()
        self.core = core

    def track_playback_ended(self, tl_track, time_position):
        # Remove old votes
        pass

    def track_playback_started(self, tl_track):
        pass
