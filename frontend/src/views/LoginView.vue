<template>
  <div class="login-container">
    <div class="login-card">
      <h2>登入</h2>
      <form @submit.prevent="login">
        <input v-model="username" placeholder="帳號" required />
        <input v-model="password" type="password" placeholder="密碼" required />
        <button type="submit" class="btn login-btn">登入</button>
      </form>
      <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
      <p>忘記密碼？<a @click.prevent="goToSendAuthentication" style="cursor: pointer; color: blue;">點此重設</a></p>
      <p>尚未註冊？<a @click.prevent="goToRegister" style="cursor: pointer; color: blue;">點此註冊</a></p>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();
const username = ref("");
const password = ref("");
const errorMessage = ref("");
const lastLogin = ref(""); 
const loginCount = ref(0); 

const login = async () => {
  errorMessage.value = "";

  try {
    console.log("發送登入請求");
    const response = await fetch("/api/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username: username.value, password: password.value }),
      mode: "cors",
      credentials: "include"
    });

    console.log("API 回應狀態碼:", response.status);
    const data = await response.json();

    if (response.ok) {
      localStorage.setItem("token", data.token);
      sessionStorage.setItem('role', data.role); 
      sessionStorage.setItem("username", username.value);
      sessionStorage.setItem("lastLogin", data.last_login);
      sessionStorage.setItem("loginCount", data.login_count);

      lastLogin.value = new Date(data.last_login).toLocaleString();
      loginCount.value = data.login_count;

      console.log("登入成功，準備跳轉到 /dashboard");
      
      await nextTick();
      console.log("儲存的 token:", localStorage.getItem("token"));

      await router.push("/dashboard");
      console.log("已跳轉到 /dashboard");
    } else {
      errorMessage.value = data.error || "登入失敗";
    }
  } catch (error) {
    errorMessage.value = "伺服器錯誤，請稍後再試";
  }
};

const goToSendAuthentication  = () => {
  router.push('/sendAuthentication')
}

const goToRegister = () => {
  router.push('/register');
};

</script>

<style scoped>

.login-container {
  display: flex;
  flex-direction: column;
  align-items: center; 
  height: 100vh; 
  justify-content: center; 
  position: relative;
  background: linear-gradient(135deg, #667eea, #764ba2); 
}

.login-card {  
  background: white;
  padding: 2rem;
  text-align: center;
  border-radius: 12px;
  box-shadow: 0 10px 10px rgba(0, 0, 0, 0.1);
  text-align: center;
  width: 320px;
  margin-bottom: 10px;
}

h2 {
  font-size: 2rem;
  font-weight: bold;
}

input {
  width: 100%;
  padding: 10px;
  margin-bottom: 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  outline: none;
  transition: all 0.3s ease;
  box-sizing: border-box;
}

input:focus {
  border-color: #007bff;
  box-shadow: 0 0 5px rgba(0, 123, 255, 0.5);
  display: flex;
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
  transition: all 0.3s ease;
}

.login-btn {
  background: #007bff;
  color: white;
}

.login-btn:hover {
  background: #0056b3;
}

.error {
  margin-top: 10px;
  color: red;
  font-weight: bold;
}

</style>
