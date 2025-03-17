<template>
    <div class="send-container">
      <h2>請輸入用戶名</h2>
      <form @submit.prevent="send">
        <input v-model="username" placeholder="帳號" required />
        <button type="submit" class="btn send-btn">輸入</button>
      </form>
      <button
        @click="verifyEmail"
        ref="verifyButton"
        class="btn Verify-Email-btn"
        :disabled="isDisabled">
        {{ buttonText }}
      </button>
      <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
      <p>不須重設？<a @click.prevent="goToLogin" style="cursor: pointer; color: blue;">點此登入</a></p>
    </div>
  </template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();
const username = ref("")
const errorMessage = ref("");
const verifyButton = ref(null);
const isDisabled = ref(false);
const buttonText = ref("驗證綁定 Email");

onMounted(() => {
  if (verifyButton.value) {
    verifyButton.value.addEventListener("click", async () => {
      if (isDisabled.value) return;

      let cooldown = 5;
      isDisabled.value = true;
      buttonText.value = `請稍候... (${cooldown})`;

      const interval = setInterval(() => {
        cooldown--;
        buttonText.value = `請稍候... (${cooldown})`;

        if (cooldown <= 0) {
          clearInterval(interval);
          isDisabled.value = false;
          buttonText.value = "驗證綁定 Email";
        }
      }, 1000);

      try {
        await verifyEmail();
      } catch (error) {
        console.error(error);
      }
    });
  }
});

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
            alert(data.message);
        }
    } catch (error) {
        errorMessage.value = "請求失敗，請稍後再試";
    }
};

const verifyEmail = async () => {
  if (isDisabled.value) return;
  let cooldown = 5;
  isDisabled.value = true;
  buttonText.value = `請稍候... (${cooldown})`;

  const interval = setInterval(() => {
    cooldown--;
    buttonText.value = `請稍候... (${cooldown})`;

    if (cooldown <= 0) {
      clearInterval(interval);
      isDisabled.value = false;
      buttonText.value = "驗證綁定 Email";
    }
  }, 1000);
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
        confirm(`綁定的 Email：${data.email}`);
    } else {
        alert(data.message);
    }
  } catch (error) {
      alert("請求失敗，請稍後再試");
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
  color: #980042;
  font-weight: bold;
}

.success {
  margin-top: 10px;
  color: green;
  font-weight: bold;
}
</style>
