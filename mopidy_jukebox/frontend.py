import pykka

from mopidy import core


class JukeboxFrontend(pykka.ThreadingActor, core.CoreListener):
    def __init__(self, config, core):
        super(JukeboxFrontend, self).__init__()
        self.core = core
