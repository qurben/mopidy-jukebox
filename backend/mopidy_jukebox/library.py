from pprint import pprint

from peewee import fn, SQL

from models import Vote


class Tracklist(object):
    """
    Tracklist works as following:
    Track with the most votes goes first. After that the track with one vote less.
    If the next track has the same number of votes, the track where the newest vote is the oldest overall wins.
    """
    @staticmethod
    def update_tracklist(tracklist):
        track_count = fn.Count(Vote.track_uri)
        newest_vote = fn.Max(Vote.timestamp)
        query = (Vote
                 .select(Vote.track_uri, track_count.alias('count'), newest_vote.alias('newest'))
                 .group_by(Vote.track_uri)
                 .order_by(-track_count, +newest_vote)) # First order by date, then by track count

        pprint(query)

        for vote in query:
            print vote.track_uri

        tracklist.clear()
        tracklist.add(uris=[vote.track_uri for vote in query])

        pprint(tracklist)