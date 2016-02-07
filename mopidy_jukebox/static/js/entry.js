import "../css/style.css"

import ko from 'knockout'

import Q from 'q'
import 'q-xhr'

class Track {
    constructor(name, uri, artists, album, images, votes, user) {
        let self = this;

        this.name = ko.observable(name);
        this.uri = ko.observable(uri);
        this.artists = ko.observable(artists);
        this.album = ko.observable(album);
        this.images = ko.observable(images);
        this.votes = ko.observableArray(votes);

        this.voted = ko.computed(() => {
            return self.votes().find((vote) => vote.uid == user().uid());
        })
    }
}

class User {
    constructor() {
        this.uid = ko.observable();
        this.name = ko.observable();
        this.email = ko.observable();
        this.picture = ko.observable();
    }

    load() {
        let self = this;
        Q.xhr.get('/jukebox-api/user')
            .then((resp) => {
                let user = resp.data;

                self.uid(user.uid);
                self.name(user.name);
                self.email(user.email);
                self.picture(user.picture);
            })
    }
}

class TracklistViewModel {
    constructor() {
        let self = this;

        this.tracks = ko.observableArray();
        this.user = ko.observable(new User());
    }

    load() {
        let self = this

        self.user().load();

        Q.xhr.get('/jukebox-api/tracklist')
            .then((resp) => {
                let tracks = [];
                for (let item of resp.data.tracklist) {
                    let track = item.track;
                    tracks.push(new Track(track.track_name, track.track_uri, track.artists, track.album, track.images, track.votes, self.user))
                }
                self.tracks(tracks);
            });
    }

    voted(track) {
        console.log(track)
        console.log(this.user())
        for (let voter of track.votes()) {
            if (voter.user == this.user().name)
                return 'hoi'
        }
        return 'doei'
    }

    vote(track) {
        let self = this;
        console.log(track)
        Q.xhr.put('/jukebox-api/vote', {
            'track': track.uri()
        }).then((resp) => {
            self.load();
        }, (err) => {
            if (err.status == 409) // Vote already exists
                console.error("Vote already exists", err);
        });
    }
}

let myTracklistViewModel = new TracklistViewModel();

window.myTracklistViewModel = myTracklistViewModel;
window.Q = Q;

myTracklistViewModel.load()


ko.applyBindings(myTracklistViewModel)