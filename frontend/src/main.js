import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import VueLazyLoad from 'vue3-lazyload'

const app = createApp(App);
app.use(VueLazyLoad, {
  loading: 'loading.gif',
  error: 'error.png'
})

app.use(router);
app.mount('#app');
