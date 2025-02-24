<template>
  <div class="login-container">
    <h2>登入</h2>
    <form @submit.prevent="login">
      <input v-model="username" placeholder="帳號" required />
      <input v-model="password" type="password" placeholder="密碼" required />
      <button type="submit">登入</button>
    </form>
    <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const username = ref('');
const password = ref('');
const errorMessage = ref('');

const login = async () => {
  try {
    // 模擬 API 請求（實際應與後端溝通）
    if (username.value === 'admin' && password.value === '1234') {
      localStorage.setItem('token', 'mock_token'); // 儲存 token
      router.push('/dashboard'); // 跳轉到儀表板
    } else {
      errorMessage.value = '帳號或密碼錯誤';
    }
  } catch (error) {
    errorMessage.value = '登入失敗，請稍後再試';
  }
};
</script>

<style>
.login-container { text-align: center; }
.error { color: red; }
</style>
