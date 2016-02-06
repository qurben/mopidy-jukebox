import "../css/style.css"

import ko from 'knockout'

import Q from 'q'
import 'q-xhr'

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
                    this.tracks(resp.data.tracklist);
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