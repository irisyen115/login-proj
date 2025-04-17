const path = require('path');

module.exports = {
  outputDir: 'dist',

  clean: false,

  chainWebpack: (config) => {
    config.entry('app').clear().add('./main.js');
  },

  devServer: {
    allowedHosts: ['irisyen115.synology.me'],
    host: '0.0.0.0',
    port: 8081
  }

};
