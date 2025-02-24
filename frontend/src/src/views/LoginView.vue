<template>
  <div class="login-container">
    <h2>登入</h2>
    <form @submit.prevent="login">
      <input v-model="email" type="email" placeholder="電子郵件" required />
      <input v-model="username" placeholder="帳號" required />
      <input v-model="password" type="password" placeholder="密碼" required />
      <button type="submit">登入</button>
      <button @click.prevent="register">註冊</button>
    </form>
    <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();
const email = ref("");
const username = ref("");
const password = ref("");
const errorMessage = ref("");

// 登入處理函數
const login = async () => {
  errorMessage.value = ""; // 清除舊的錯誤訊息

  try {
    const response = await fetch("/api/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: email.value, username: username.value, password: password.value }), // 加入電子郵件欄位
    });

    const data = await response.json();

    if (response.ok) {
      localStorage.setItem("token", data.token); // 儲存後端提供的 token
      router.push("/dashboard"); // 跳轉到儀表板
    } else {
      errorMessage.value = data.error || "登入失敗";
    }
  } catch (error) {
    errorMessage.value = "伺服器錯誤，請稍後再試";
  }
};

// 註冊處理函數
const register = async () => {
  errorMessage.value = ""; // 清除舊的錯誤訊息

  try {
    const response = await fetch("/api/register", {  // 註冊的 API 端點
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: email.value, username: username.value, password: password.value }), // 加入電子郵件欄位
    });

    const data = await response.json();

    if (response.ok) {
      localStorage.setItem("token", data.token); // 儲存後端提供的 token
      router.push("/dashboard"); // 跳轉到儀表板
    } else {
      errorMessage.value = data.error || "註冊失敗";
    }
  } catch (error) {
    errorMessage.value = "伺服器錯誤，請稍後再試";
  }
};
</script>

<style>
.login-container {
  text-align: center;
}
.error {
  color: red;
}
</style>
