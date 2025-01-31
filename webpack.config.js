const argv = require('yargs').argv;
const paths = require('./build/paths');

// Set isProduction based on environment or argv.
let isProduction = process.env.NODE_ENV === 'production';
if (argv.production) {
    isProduction = true;
}

/**
 * Webpack configuration
 * Run using "webpack" or "npm run build"
 */
module.exports = {
    // Entry points locations.
    entry: {
        [`${paths.package.name}-js`]: `${__dirname}/${paths.jsEntry}`,
    },

    // (Output) bundle locations.
    // (Output) bundle locations.
    output: {
        path: __dirname + '/' + paths.jsDir,
        filename: '[name].js', // file
        chunkFilename: '[name].bundle.js',
        publicPath: '/static/bundles/',
    },
    // Modules
    module: {
        rules: [
            // .js
            {
                test: /.js?$/,
                exclude: /node_modules/,
                loader: 'babel-loader',
            },
        ]
    },

    // Use --production to optimize output.
    mode: isProduction ? 'production' : 'development',

    // Use --sourcemap to generate sourcemap.
    devtool: argv.sourcemap ? 'sourcemap' : false,
};
