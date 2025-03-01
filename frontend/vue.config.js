// vue.config.js
module.exports = {
    chainWebpack: (config) => {
      // 設定入口路徑
      config.entry('app').clear().add('./main.js'); // 確保這裡是新的 src/main.js 路徑
    },
    configureWebpack: {
      // 其他 Webpack 配置
    },
  };
  