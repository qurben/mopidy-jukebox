import "../css/style.css"

import ko from 'knockout'

import oboe from 'oboe'

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
        oboe('/jukebox-api/user')
            .done((user) => {
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

        this.vote = (track) => {
            console.log(self);
            if (track.voted()) {
                oboe({
                    'url': '/jukebox-api/vote',
                    'method': 'DELETE',
                    'body': {
                        'track': track.uri()
                    }
                }).done((resp) => {
                    self.load();
                }).fail((err) => {
                    if (err.status == 404) // Vote not deleted
                        console.error("Vote not deleted", err);
                })
            } else {
                oboe({
                    'url': '/jukebox-api/vote',
                    'method': 'PUT',
                    'body': {
                        'track': track.uri()
                    }
                }).done((resp) => {
                    self.load();
                }).fail((err) => {
                    if (err.status == 409) // Vote already exists
                        console.error("Vote already exists", err);
                })
            }
        }

        this.load = () => {
            self.user().load();

            oboe('/jukebox-api/tracklist')
                .done((resp) => {
                    let tracks = [];
                    for (let item of resp.tracklist) {
                        let track = item.track;
                        tracks.push(new Track(track.track_name, track.track_uri, track.artists, track.album, track.images, track.votes, self.user))
                    }
                    self.tracks(tracks);
                });
        };

        this.voted = (track) => {
            for (let voter of track.votes()) {
                if (voter.user == this.user().name)
                    return true
            }
            return false
        }
    }
}

let myTracklistViewModel = new TracklistViewModel();

window.myTracklistViewModel = myTracklistViewModel;
window.Q = Q;

myTracklistViewModel.load();


ko.applyBindings(myTracklistViewModel)