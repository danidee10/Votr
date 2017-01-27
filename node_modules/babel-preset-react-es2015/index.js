var es2015 = require('babel-preset-es2015');
var react = require('babel-preset-react');

module.exports = {
    plugins: [].concat.call(react.plugins, es2015.plugins)
};