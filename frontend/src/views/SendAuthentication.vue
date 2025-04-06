<template>
  <div class="send-container">
    <h2>請輸入用戶名</h2>
    <div class="send-card">
      <form @submit.prevent="send">
        <input v-model="username" placeholder="帳號" required />
        <button type="submit" class="btn send-btn" >發送重設頁面</button>
      </form>
      <button @click="verifyEmail" class="btn Verify-Email-btn">驗證綁定 Email</button>
      <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
    </div>
    <p>不須重設？<a @click.prevent="goToLogin" style="cursor: pointer; color: blue;">點此登入</a></p>
    <div v-if="showVerification" class="verification-container">
      <h3>請輸入發送到您的 Email 的驗證碼</h3>
      <input v-model="verificationCode" placeholder="驗證碼" required />
      <button @click="verifyCode" class="btn send-btn">驗證碼確認</button>
      <p v-if="verificationError" class="error">{{ verificationError }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();
const username = ref("");
const errorMessage = ref("");
const emailVerify = ref(false);
const verificationCode = ref("");
const showVerification = ref(false);
const verificationError = ref("");

const verifyEmail = async () => {
  try {
    const response = await fetch("/api/verify-email", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username: username.value }),
      mode: "cors",
      credentials: "include"
    });
    const data = await response.json();

    if (response.ok) {
      confirm(data.message);
      showVerification.value = true;
    } else {
      alert(data.error)
    }

  } catch (error) {
    alert("請求失敗，請稍後再試");
  }
};

const verifyCode = async () => {
  try {
    const response = await fetch("/api/verify-code", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username: username.value, verificationCode: verificationCode.value }),
      mode: "cors",
      credentials: "include"
    });
    const data = await response.json();

    if (response.ok) {
      emailVerify.value = true;
      showVerification.value = false;
      confirm(data.message);
    } else {
      alert(data.error);
    }
  } catch (error) {
    verificationError.value = "驗證碼驗證失敗，請稍後再試";
  }
};

const send = async () => {
  console.log("發送按鈕已點擊");
  console.log(emailVerify)

  if (emailVerify.value == false) {
    errorMessage.value = "請先驗證綁定的 Email 再發送重設頁面"
    alert("請先驗證綁定的 Email 再發送重設頁面");
    return;
  }

  try {
    const response = await fetch("/api/send-authentication", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username: username.value }),
      mode: "cors",
      credentials: "include"
    });

    if (response.ok) {
      if (confirm("驗證信已發送至綁定 email，請簽收，請勿重複點取") == true) {
        router.push('/login');
      }
    } else {
      const data = await response.json();
      alert(data.message);
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
  background-color: wheat;
  display: flex;
  padding: 2rem;
  text-align: center;
  flex-direction: column;
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

.send-btn {
  background: #007bff;
  color: white;
}

.send-btn:hover {
  background: #0056b3;
}

.Verify-Email-btn {
  background: #28a745;
  color: white;
}

.Verify-Email-btn:hover {
  background: #218838;
}

.error {
  margin-top: 10px;
  color: #ff006f;
  font-weight: bold;
  font-size: medium;
}

.verification-container {
  background-color: wheat;
  padding: 2rem;
  text-align: center;
  flex-direction: column;
  border-radius: 12px;
  box-shadow: 0 10px 10px rgba(0, 0, 0, 0.1);
  width: 320px;
  margin-top: 20px;
}
</style>
