var p = require('path');

module.exports = {
    context: p.join(__dirname, 'mopidy_jukebox', 'static'),
    entry: '.' + p.sep + 'js' + p.sep + 'entry.js',
    output: {
        path: p.join(__dirname, 'mopidy_jukebox', 'static', 'dist'),
        filename: "bundle.js",
    },
    module: {
        loaders: [
            {
                test: /\.css$/,
                loader: "style!css"
            },
            {
                test: /\.js?$/,
                exclude: /(node_modules|bower_components)/,
                loader: 'babel', // 'babel-loader' is also a legal name to reference
                query: {
                    presets: ['react', 'es2015']
                }
            }
        ]
    },
    resolve: {
        modulesDirectories: ['node_modules']
    },
    devtool: "eval-source-map"
};
