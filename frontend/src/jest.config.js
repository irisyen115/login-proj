module.exports = {
  testEnvironment: 'jsdom',

  transform: {
    '^.+\\.vue$': 'vue-jest',
    '^.+\\.js$': 'babel-jest',
  },
  moduleFileExtensions: [
    'js',
    'json',
    'vue',
  ],
  moduleNameMapper: {
    "^axios$": require.resolve("axios"),
  },
  transformIgnorePatterns: [
    'node_modules/(?!(@vue|vue-router)/)',
    "/node_modules/(?!axios)", 
  ],
};
