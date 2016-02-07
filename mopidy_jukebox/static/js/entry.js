import "../css/style.css"

import ko from 'knockout'

import Q from 'q'
import 'q-xhr'

class Track {
    constructor(name, uri, artists, album, images, votes) {
        this.name = ko.observable()
        this.uri = ko.observable()
        this.artists = ko.observable()
        this.album = ko.observable()
        this.images = ko.observable()
        this.votes = ko.observableArray()
    }
}

class TracklistViewModel {
    constructor() {
        this.tracks = ko.observableArray();
    }

    vote(track) {
        Q.xhr.put('/jukebox-api/vote', {
            'track': track.track_uri
        }).then((resp) => {
            Q.xhr.get('/jukebox-api/tracklist')
                .then((resp) => {
                    tracks = []
                    for (let track of resp.data.tracklist) {
                        tracks.push(new Track(track.track_name, track.track_uri, track.artists, track.album, track.images, track.votes))
                    }
                    this.tracks(tracks);
                });
        }, (err) => {
            if (err.status == 409) // Vote already exists
                console.error(err);
        });
    }
}

let myTracklistViewModel = new TracklistViewModel();

Q.xhr.get('/jukebox-api/tracklist')
    .then((resp) => {
        myTracklistViewModel.tracks(resp.data.tracklist);
    });

ko.applyBindings(myTracklistViewModel)