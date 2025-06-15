module.exports = {
  root: true,
  env: {
    node: true,
  },
  parser: 'vue-eslint-parser', // 讓 ESLint 用 vue-eslint-parser 解析 .vue 文件
  parserOptions: {
    parser: '@babel/eslint-parser', // 內部用 @babel/eslint-parser 解析 script 區塊
    requireConfigFile: false, // 如果你沒有 babel config，這行很重要
    ecmaVersion: 2020,
    sourceType: 'module',
  },
  extends: [
    'eslint:recommended',
    'plugin:vue/essential',
  ],
  rules: {
    // 你的規則
  },
};
