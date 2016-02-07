from models import Vote


def votes_json(track):
    votes = Vote.select().where(Vote.track_uri == track.uri)

    for vote in votes:
        yield {
            'user': vote.user.name,
            'picture': vote.user.picture,
            'time': vote.timestamp.isoformat()
        }


def track_json(track):
    """
    Generate JSON from a Mopidy track
    :param track: A mopidy.models.Track
    :return:
    """
    return {
        'track_name': track.name,
        'track_uri': track.uri,
        'artists': [artist.name for artist in track.artists],
        'album': track.album.name,
        'images': [image for image in track.album.images],
        'votes': list(votes_json(track))
    }
