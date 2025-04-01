<template>
  <div class="login-container">
    <div class="login-card">
    <h2>綁定帳戶</h2>
    <form @submit.prevent="bindEmail">
      <input v-model="email" type="email" placeholder="請輸入 Email" required />
      <button type="submit" class="btn login-btn">綁定</button>
    </form>
    <p v-if="message" class="success">{{ message }}</p>
    <p v-if="error" class="error">{{ error }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";

const uid = ref("");
const email = ref("");
const message = ref("");
const error = ref("");

onMounted(() => {
  const params = new URLSearchParams(window.location.search);
  uid.value = params.get("uid") || "";
});

const bindEmail = async () => {
  error.value = "";
  message.value = "";

  try {
    const response = await fetch("/api/bind-email", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ uid: uid.value, email: email.value })
    });

    const data = await response.json();
    if (response.ok) {
      message.value = "綁定成功！請檢查您的 Email";
    } else {
      error.value = data.error || "綁定失敗";
    }
  } catch {
    error.value = "伺服器錯誤，請稍後再試";
  }
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
  background: linear-gradient(135deg, #66ea92, #4b9ca2);
}

.login-card {
  background: white;
  padding: 2rem;
  text-align: center;
  border-radius: 12px;
  box-shadow: 0 10px 10px rgba(0, 0, 0, 0.1);
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
}

input:focus {
  border-color: #007bff;
}

.btn {
  width: 100%;
  padding: 10px;
  margin-top: 8px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
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
