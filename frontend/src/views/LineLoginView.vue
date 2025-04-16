<template>
  <div class="login-container">
    <div class="login-card">
      <h2>登入</h2>
      <form @submit.prevent="bindEmail">
        <input v-model="username" placeholder="帳號" required />
        <input v-model="password" type="password" placeholder="密碼" required />
        <button type="submit" class="btn login-btn">登入</button>
      </form>
      <div id="google-signin-button"></div>
      <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
      <p>忘記密碼？<a @click.prevent="goToSendAuthentication" style="cursor: pointer; color: blue;">點此重設</a></p>
      <p>尚未註冊？<a @click.prevent="goToRegister" style="cursor: pointer; color: blue;">點此註冊</a></p>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();
const uid = ref("");
const username = ref("");
const password = ref("");
const errorMessage = ref("");

onMounted(() => {
  const params = new URLSearchParams(window.location.search);
  uid.value = params.get("uid") || "";
});

const bindGoogleEmail = async (googleToken) => {
  try {
    const response = await fetch("/api/bind-google-email", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ google_token: googleToken, uid: uid.value }),
      mode: "cors",
      credentials: "include"
    });

    console.log("API 回應狀態碼:", response.status);
    const data = await response.json();

    if (response.ok) {
      localStorage.setItem("token", data.token);
      sessionStorage.setItem('role', data.role);
      sessionStorage.setItem("username", data.username);
      sessionStorage.setItem("lastLogin", data.last_login);

      console.log("登入成功，準備跳轉到 /dashboard");
      await router.push("/dashboard");
    } else {
      errorMessage.value = data.error;
    }
  } catch (error) {
    errorMessage.value = "伺服器錯誤，請稍後再試";
  }
};

const bindEmail = async () => {
  errorMessage.value = "";
  try {
    console.log("發送登入請求");

    const response = await fetch("/api/bind-email", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ uid: uid.value, username: username.value, password: password.value }),
      mode: "cors",
      credentials: "include"
    });

    console.log("API 回應狀態碼:", response.status);
    const data = await response.json();

    if (response.ok) {
      localStorage.setItem("token", data.token);
      sessionStorage.setItem('role', data.role);
      sessionStorage.setItem("username", data.username);
      sessionStorage.setItem("lastLogin", data.last_login);

      console.log("登入成功，準備跳轉到 /dashboard");
      await router.push("/dashboard");
      console.log("已跳轉到 /dashboard");
    } else {
      errorMessage.value = data.error;
    }
  } catch (error) {
    errorMessage.value = "伺服器錯誤，請稍後再試";
  }
};

const initializeGoogleSignIn = () => {
  if (!window.google || !google.accounts) {
    console.error("Google Sign-In API 未載入，將稍後重試...");
    setTimeout(initializeGoogleSignIn, 1000);
    return;
  }

  google.accounts.id.initialize({
    client_id: "825100576956-ia8d4ulk2dapck8f3h5jmr10p14uf54q.apps.googleusercontent.com",
    callback: handleCredentialResponse,
  });

  nextTick(() => {
    const button = document.getElementById("google-signin-button");
    if (button) {
      google.accounts.id.renderButton(button, { theme: "outline", size: "large" });
    } else {
      console.error("找不到 Google Sign-In 按鈕");
    }
  });
};

const handleCredentialResponse = (response) => {
  try {
    if (!response || !response.credential) {
      console.error("Google 登入失敗: 無效的 credential");
      return;
    }

    const idToken = response.credential;
    console.log("收到的 Google id_token:", idToken);

    bindGoogleEmail(idToken);
  } catch (error) {
    console.error("處理 Google 登入回應時發生錯誤:", error);
  }
};

onMounted(() => {
  console.log("onMounted 執行，開始初始化 Google Sign-In");
  initializeGoogleSignIn();
});

const goToSendAuthentication = () =>{
  router.push('/sendAuthentication')
}

const goToRegister = () =>{
  router.push('/register')
}

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
