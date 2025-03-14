<template>
    <div class="send-container">
      <h2>請輸入用戶名</h2>
      <form @submit.prevent="send">
        <input v-model="username" placeholder="帳號" required />
        <button type="submit" class="btn Send-Authentication-btn">輸入</button>
      </form>
      <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
      <p>不須重設？<a @click.prevent="goToLogin" style="cursor: pointer; color: blue;">點此登入</a></p>
    </div>
  </template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();
const username = ref("")
const errorMessage = ref("");

const send = async () => {
    try {
        const response = await fetch("/api/send-authentication", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username: username.value }),
            mode: "cors",
            credentials: "include"
        });

        if (response.ok) {
            if (confirm("驗證信已發送至綁定 email，請簽收") == true) {
              router.push('/login')
            }
        } else {
            const data = await response.json();
            errorMessage.value = "伺服器錯誤，請稍後再試";
        }
    } catch (error) {
        errorMessage.value = "請求失敗，請稍後再試";
    }
};
const goToLogin = () => {
  router.push('/login');
};
</script>

<style scoped>
.send-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 100vh;
  justify-content: center;
  background: linear-gradient(135deg, #eaac66, #f33838);
}

.send-card {
  background: white;
  padding: 2rem;
  text-align: center;
  border-radius: 12px;
  box-shadow: 0 10px 10px rgba(0, 0, 0, 0.1);
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
  border: 1px solid #ddd;
  border-radius: 8px;
  outline: none;
  transition: all 0.3s ease;
  box-sizing: border-box;
}

input:focus {
  border-color: #007bff;
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

.Send-Authentication-btn {
  background: #007bff;
  color: white;
}

.Send-Authentication-btn:hover {
  background: #0056b3;
}

.error {
  margin-top: 10px;
  color: red;
  font-weight: bold;
}
</style>
