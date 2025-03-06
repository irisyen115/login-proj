import { createRouter, createWebHistory } from 'vue-router';
import LoginView from '../views/LoginView.vue'; 
import RegisterView from '../views/RegisterView.vue'; 
import DashboardView from '../views/DashboardView.vue'; 


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
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  const isAuthenticated = localStorage.getItem('token');
  console.log("目前 token:", isAuthenticated); 
  if (!isAuthenticated && to.name !== 'login' && to.name !== 'register') {
    console.log("未認證，跳轉回登入頁面");
    next('/login');
  } else {
    console.log("已認證，正常跳轉");
    next();
  }

  const token = localStorage.getItem("token");

  if (token && (to.path === '/login' || to.path === '/register')) {
    next('/dashboard');
  } else {
    next();
  }

});


export default router;
