<template>
    <div class="login-container">
      <div class="login-card">
        <h2>註冊</h2>
        <form @submit.prevent="login">
          <!-- <input v-model="email" type="email" placeholder="電子郵件" required /> -->
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
  // const email = ref("");
  const username = ref("");
  const password = ref("");
  const errorMessage = ref("");
    
  // 註冊處理函數
  const register = async () => {
    errorMessage.value = ""; // 清除舊的錯誤訊息
  
    try {
      const response = await fetch("/api/register", {  // 註冊的 API 端點
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: username.value, password: password.value }), // 加入電子郵件欄位
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

  const goToLogin = () => {
    router.push('/login');
  };
  </script>
  
  <style scoped>
  
  /* 讓登入介面置中 */
  .login-container {
  display: flex;
  flex-direction: column;
  align-items: center; /* 水平置中 */
  height: 100vh; /* 讓區塊高度充滿整個視窗 */
  justify-content: center; /* 讓表單垂直置中 */
  position: relative;
  background: linear-gradient(135deg, #ea669d, #764ba2); 
}

/* 卡片樣式 */
.login-card {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  text-align: center;
  width: 320px;
  margin-bottom: 10px;
}

/* 標題 */
h2 {
  position: absolute;
  top: 20px; /* 距離頁面頂部 20px */
  left: 50%;
  transform: translateX(-50%); /* 水平置中 */
  font-size: 2rem;
  font-weight: bold;
}

/* 輸入框樣式 */
input {
  width: 100%;
  padding: 10px;
  margin-bottom: 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  outline: none;
  transition: all 0.3s ease;
}
  
  input:focus {
    border-color: #007bff;
    box-shadow: 0 0 5px rgba(0, 123, 255, 0.5);
  }
  
  /* 按鈕樣式 */
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
  
  .register-btn {
    background: #28a745;
    color: white;
  }
  
  .register-btn:hover {
    background: #1e7e34;
  }
  
  /* 錯誤訊息 */
  .error {
    margin-top: 10px;
    color: red;
    font-weight: bold;
  }
  </style>
  