var p = require('path');

module.exports = {
    context: p.join(__dirname, 'mopidy_jukebox', 'static'),
    entry: '.' + p.sep + 'entry.js',
    output: {
        path: p.join(__dirname, 'mopidy_jukebox','static','dist'),
        filename: "bundle.js"
    },
    module: {
        loaders: [
            { test: /\.css$/, loader: "style!css" }
        ]
    }
};
