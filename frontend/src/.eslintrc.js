module.exports = {
  root: true,
  env: {
    browser: true,
    node: true,
    es2021: true,
  },
  parser: '@babel/eslint-parser',
  parserOptions: {
    requireConfigFile: false, // 如果你沒有 babel.config.js，可加這行
    ecmaVersion: 2021,
    sourceType: 'module',
    babelOptions: {
      presets: ['@babel/preset-env'],
    },
  },
  extends: [
    'eslint:recommended',
    'plugin:vue/vue3-recommended', // Vue 2 用這個，如果是 Vue 3 用 'plugin:vue/vue3-recommended'
  ],
  plugins: [
    'vue'
  ],
  rules: {
    // 在這裡自訂規則，例如：
    'no-console': process.env.NODE_ENV === 'production' ? 'warn' : 'off',
    'no-debugger': process.env.NODE_ENV === 'production' ? 'warn' : 'off',
  }
}

