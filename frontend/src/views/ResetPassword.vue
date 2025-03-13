<template>
  <div class="reset-password-container">
    <div class="reset-password-card">
      <h2>重設密碼</h2>
      <form @submit.prevent="resetPassword">
        <div>
          <input
            type="text"
            v-model="username"
            placeholder="請輸入帳號"
            required
            :disabled="isLoading"
          />
        </div>
        <div>
          <input
            type="password"
            v-model="newPassword"
            placeholder="請輸入新密碼"
            required
            :disabled="isLoading"
          />
        </div>
        <button type="submit" class="btn reset-btn" :disabled="isLoading">
          {{ isLoading ? "重設中..." : "重設密碼" }}
        </button>
      </form>
      <p>已有帳號？<a @click.prevent="goToLogin" style="cursor: pointer; color: blue;">點此登入</a></p>
      <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter, useRoute } from "vue-router";

const router = useRouter();
const username = ref("");
const newPassword = ref("");
const errorMessage = ref("");
const isLoading = ref(false);
const route = useRoute();
const keyCertificate = route.query.key;

const resetPassword = async () => {
  errorMessage.value = "";
  isLoading.value = true;

  try {
    const response = await fetch(`/api/reset-password/${keyCertificate}` , {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        username: username.value,
        password: newPassword.value,
      }),
      mode: "cors",
      credentials: "include",
    });

    const data = await response.json();

    if (response.ok) {
      router.push("/login");
      alert("密碼重設成功，請重新登入");
    } else {
      errorMessage.value = data.error || "密碼重設失敗";
    }
  } catch (error) {
    errorMessage.value = "伺服器錯誤，請稍後再試";
  } finally {
    isLoading.value = false;
  }
};

const goToLogin = () => {
  router.push('/login');
};
</script>

<style scoped>
.reset-password-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 100vh;
  justify-content: center;
  background: linear-gradient(135deg, #66eacd, #4b9ca2);
}

.reset-password-card {
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

.reset-btn {
  background: #007bff;
  color: white;
}

.reset-btn:hover {
  background: #0056b3;
}

.error {
  margin-top: 10px;
  color: red;
  font-weight: bold;
}
</style>
