import "../css/style.css"

import ko from 'knockout'

import Q from 'q'
import 'q-xhr'

class TracklistViewModel {
    constructor() {
        this.tracks = ko.observableArray();
    }
}

let myTracklistViewModel = new TracklistViewModel();

Q.xhr.get('/jukebox-api/tracklist')
    .then((resp) => {
        myTracklistViewModel.tracks(resp.data.tracklist);
    });

ko.applyBindings(myTracklistViewModel)