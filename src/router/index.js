import { createRouter, createWebHistory } from 'vue-router';
import LoginView from '../views/LoginView.vue';  // 載入登入頁面
import DashboardView from '../views/DashboardView.vue';  // 載入儀表板頁面

const routes = [
  {
    path: '/',
    name: 'home',
    redirect: '/login',  // 根目錄會重定向到登入頁面
  },
  {
    path: '/login',
    name: 'login',
    component: LoginView,
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
  console.log("目前 token:", isAuthenticated);  // 記錄 token 狀態
  if (to.name !== 'login' && !isAuthenticated) {
    console.log("未認證，跳轉回登入頁面");
    next('/login');
  } else {
    console.log("已認證，正常跳轉");
    next(); // 允許跳轉
  }
});


export default router;
