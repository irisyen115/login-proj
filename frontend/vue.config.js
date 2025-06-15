const ESLintPlugin = require('eslint-webpack-plugin');
const path = require('path');

module.exports = {
  chainWebpack: config => {
    config.plugin('eslint').tap(args => {
      // 移除 extensions 選項（eslint-webpack-plugin 4 以後不支援這個）
      if (args[0].extensions) {
        delete args[0].extensions;
      }
      return args;
    });
  },
};
