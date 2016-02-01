def track_json(track):
    """
    Generate JSON from a Mopidy track
    :param track: A mopidy.models.Track
    :return:
    """
    return {
        'track_name': track.name,
        'artists': [artist.name for artist in track.artists],
        'album': track.album.name
    }
