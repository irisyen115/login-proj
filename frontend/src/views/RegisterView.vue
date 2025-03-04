<template>
  <div class="register-container">
    <div class="register-card">
      <h2>註冊</h2>
      <form @submit.prevent="register">
        <input v-model="username" placeholder="帳號" required />
        <input v-model="password" type="password" placeholder="密碼" required />
        <button @click.prevent="register" class="btn register-btn">註冊</button>
      </form>

      <p v-if="errorMessage" class="error">{{ errorMessage }}</p>

      <p>已有帳號？<a @click.prevent="goToLogin" style="cursor: pointer; color: blue;">點此登入</a></p>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();
const username = ref("");
const password = ref("");
const errorMessage = ref("");

const register = async () => {
  errorMessage.value = "";

  if (!username.value || !password.value) {
    errorMessage.value = "帳號和密碼不能為空";
    return;
  }

  try {
    const response = await fetch("/api/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ 
        username: username.value, 
        password: password.value 
      }),
      credentials: "include",
    });

    const data = await response.json();    

    if (response.ok) {
      sessionStorage.setItem("username", username.value);
      router.push('/dashboard');

    } else {
      errorMessage.value = data.error || "註冊失敗";
    }
  } catch (error) {
    errorMessage.value = "伺服器錯誤，請稍後再試";
  }
};

const goToLogin = () => {
  router.push('/login');
};
</script>

<style>
.register-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 100vh;
  justify-content: center;
  background: linear-gradient(135deg, #ea669d, #764ba2);
}

.register-card {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  text-align: center;
  width: 320px;
}

h2 {
  font-size: 2rem;
  font-weight: bold;
}

input {
  width: 100%;
  padding: 10px;
  margin-bottom: 12px;
  justify-content: center;
  border: 1px solid #ddd;
  border-radius: 8px;
  outline: none;
}

input:focus {
  border-color: #007bff;
  justify-content: center;
  box-shadow: 0 0 5px rgba(0, 123, 255, 0.5);
}

.btn {
  width: 100%;
  padding: 10px;
  margin-top: 8px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
}

.register-btn {
  background: #28a745;
  color: white;
}

.register-btn:hover {
  background: #1e7e34;
}

.error {
  margin-top: 10px;
  color: red;
  font-weight: bold;
}

.success {
  margin-top: 10px;
  color: green;
  font-weight: bold;
}
</style>
