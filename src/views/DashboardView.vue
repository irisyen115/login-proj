<template>
  <div>
    <h2>歡迎來到儀表板</h2>
    <button @click="logout">登出</button>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router';
import { defineProps, defineExpose } from 'vue';

// 假設有 message 這個 prop
const props = defineProps({
  message: String,
});

const router = useRouter();

const logout = () => {
  localStorage.removeItem('token');
  router.push('/');
};

// 只需調用一次 defineProps，並且在這裡暴露 logout 方法
defineExpose({
  logout
});
</script>
