<template>
  <div>
    <h2>登入/註冊成功</h2>
    <div v-if="lastLogin && loginCount !== null">
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
const lastLogin = ref(null);  // ✅ 設定為響應式數據
const loginCount = ref(null); // ✅ 設定為響應式數據

const logout = () => {
  localStorage.removeItem('token');
  sessionStorage.removeItem('lastLogin');
  sessionStorage.removeItem('loginCount');
  router.push('/');
};

onMounted(() => {
  const storedLoginTime = sessionStorage.getItem('lastLogin');
  const storedLoginCount = sessionStorage.getItem('loginCount');

  if (storedLoginTime) {
    lastLogin.value = new Date(storedLoginTime).toLocaleString(); // ✅ 確保格式正確
  } else {
    lastLogin.value = "無登入記錄";
  }

  if (storedLoginCount) {
    loginCount.value = parseInt(storedLoginCount, 10); // ✅ 確保是數字
  } else {
    loginCount.value = 0; // 設定預設值
  }
});

defineExpose({
  logout
});
</script>
