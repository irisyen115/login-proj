<template>
  <div class="dash-container">
    <h2>登入/註冊成功</h2>
    <div v-if="username && lastLogin && loginCount !== null" class="dash-card">
      <p>用戶: {{ username }}</p>
      <p>最後登入時間: {{ lastLogin }}</p>
      <p>登入次數: {{ loginCount }}</p>
    </div>
    <button @click="logout">登出</button>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router';
import { ref, onMounted } from 'vue';

const router = useRouter();
const username = ref('');
const lastLogin = ref(null); 
const loginCount = ref(null);

const logout = () => {
  localStorage.removeItem('token');
  sessionStorage.removeItem('username');
  sessionStorage.removeItem('lastLogin');
  sessionStorage.removeItem('loginCount');
  router.push('/');
};

onMounted(() => {
  username.value = sessionStorage.getItem('username');
  const storedLoginTime = sessionStorage.getItem('lastLogin');
  const storedLoginCount = sessionStorage.getItem('loginCount');

  if (storedLoginTime) {
    lastLogin.value = new Date(storedLoginTime).toLocaleString();
  } else {
    lastLogin.value = "無登入記錄";
  }

  if (storedLoginCount) {
    loginCount.value = parseInt(storedLoginCount, 10); 
  } else {
    loginCount.value = 0; 
  }
});

defineExpose({
  logout
});
</script>

<style>
.dash-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 100vh;
  justify-content: center;
  position: relative;
  background: linear-gradient(135deg, #ea669d, #fceb05); 
}

.dash-card {
  background: rgb(82, 157, 255);
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  text-align: center;
  width: 320px;
  margin-bottom: 10px;
  font-size: larger;
}

</style>