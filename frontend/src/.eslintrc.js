module.exports = {
    extends: [
      'plugin:vue/vue3-essential', // 使用 Vue 3 配置
      'eslint:recommended'         // 使用 ESLint 推薦的基本規則
    ],
    plugins: ['vue'],              // 使用 Vue 插件
    parserOptions: {
      parser: 'babel-eslint',      // 使用 babel-eslint 解析器
    },
    rules: {
      'no-unused-vars': 'off',     // 關閉 no-unused-vars 規則
      'no-undef': 'off',           // 關閉 no-undef 規則
    },
  };
  