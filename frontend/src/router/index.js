import { createRouter, createWebHistory } from 'vue-router';
import LoginView from '../views/LoginView.vue'; 
import RegisterView from '../views/RegisterView.vue'; 
import DashboardView from '../views/DashboardView.vue'; 
import ResetPassword from '../views/ResetPassword.vue';

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
    path: '/resetPassword',
    name: 'resetPassword',
    component: ResetPassword,
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
