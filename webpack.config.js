var webpack = require('webpack')
var path = require('path');

module.exports = {
  entry: {
        header_assets: "./index.js",
        react_components: "./static/js/polls.jsx",
  },
  output: {
        path: path.join(__dirname, "static", "prod"),
        filename: "[name].js"
  },
  module: {
    loaders: [{
      test: /\.jsx?$/,
      exclude: /node_modules/,
      loader: 'babel',
      query: {
        presets: ['es2015', 'react']
      }
    },
    {
      test: /\.css$/,
      loader: "style-loader!css-loader" },
    {
      test: /\.(ttf|eot|svg|woff(2)?)(\?[a-z0-9=&.]+)?$/,
      emitFile: false,
      loader : 'url-loader?emitFile=false'
    },
    {
      test: /\.(jpg|png)?$/,
      loader: 'file-loader?emitFile=false'

    }]
  },
  resolve: {
    extensions: ['', '.js', '.jsx'],
  },

  plugins: [

    new webpack.DefinePlugin({
    'process.env': {
      NODE_ENV: JSON.stringify('production')
      }
    }),

    new webpack.optimize.UglifyJsPlugin({
      compress: {
        warnings: true
      }
    })
  ]
};
