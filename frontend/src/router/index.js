import { createRouter, createWebHistory } from 'vue-router';
import LoginView from '../views/LoginView.vue';
import RegisterView from '../views/RegisterView.vue';
import DashboardView from '../views/DashboardView.vue';
import ResetPassword from '../views/ResetPassword.vue';
import SendAuthentication from '../views/SendAuthentication.vue'
import LineLoginView from '../views/LineLoginView.vue';
import PhotoBoardView from '../views/PhotoBoardView.vue';
import BatchView from '../views/BatchView.vue';

const routes = [
  {
    path: '/',
    name: 'home',
    redirect: '/login',
  },
  {
    path: '/login',
    name: 'login',
    component: LoginView,
  },
  {
    path: '/Line-login',
    name: 'Line-login',
    component: LineLoginView,
  },
  {
    path: '/register',
    name: 'register',
    component: RegisterView,
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: DashboardView,
  },
  {
    path: '/photoBoard',
    name: 'photoBoard',
    component: PhotoBoardView,
  },
  {
    path: '/batch',
    name: 'batch',
    component: BatchView,
  },
  {
    path: '/reset-password/:key_certificate',
    name: 'resetPassword',
    component: ResetPassword,
  },
  {
    path: '/sendAuthentication',
    name: 'sendAuthentication',
    component: SendAuthentication,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, from, next) => {

  const token = localStorage.getItem("token");

  if (token && (to.name !== 'dashboard' )) {
    next('/dashboard');
  } else {
    next();
  }

});


export default router;
