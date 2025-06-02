// vue.config.js
module.exports = {
  chainWebpack: (config) => {
    config.entry('app').clear().add('./main.js')
  },
  configureWebpack: {
    // 其他 Webpack 配置
  },
  devServer: {
    proxy: {
      '/delete_photo': {
        target: 'https://irisyen115.synology.me/delete_photo', // Flask API 的位置
        changeOrigin: true,
      },
    },
  },
};
