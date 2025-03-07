<template>
  <div class="dash-container">
    <h2>登入/註冊成功</h2>

    <div v-if="role === 'admin'">
      <h3>管理員功能</h3>
      <p>您擁有管理員權限，可以查看所有使用者的資料。</p>      
    </div>

    <div v-else-if="role === 'user'">
      <h3>普通用戶功能</h3>
      <p>您是普通用戶，您只能查看自己的資料。</p>
    </div>

    <div class="avatar-container">
      <img v-if="avatarUrl" :src="avatarUrl" class="avatar-preview" alt="大頭貼">
      <p v-else>尚未上傳大頭貼</p>
      <input type="file" @change="handleFileChange" accept="image/*">
      <button @click="uploadAvatar">上傳大頭貼</button>
    </div>


    <table class="dash-table">
      <thead>
        <tr>
          <th>用戶</th>
          <th>最後登入時間</th>
          <th>登入次數</th>
          <th>權限</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="user in users" :key="user.username">
          <td>{{ user.username }}</td>
          <td>{{ user.last_login }}</td>
          <td>{{ user.login_count }}</td>
          <td>{{ user.role }}</td>
        </tr>
      </tbody>
    </table>

    <button @click="logout">登出</button>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router';
import { ref, onMounted } from 'vue';

const axios = require('axios').default;
const router = useRouter();
const username = ref('');
const lastLogin = ref(null); 
const loginCount = ref(null);
const role = ref(null);
const users = ref([]);
const avatarFile = ref(null);
const avatarUrl = ref(null);


const logout = () => {
  localStorage.removeItem('token');
  sessionStorage.clear(); 
  console.log("登出後 role:", sessionStorage.getItem('role'));

  router.push('/'); 
};

const handleFileChange = (event) => {
  const file = event.target.files[0];
  if (file) {
    avatarFile.value = file;
    avatarUrl.value = URL.createObjectURL(file); 
  }
};

const uploadAvatar = async () => {
  if (!avatarFile.value) {
    alert("請選擇圖片後再上傳！");
    return;
  }

  const formData = new FormData();
  formData.append('file', avatarFile.value);
  
  try {
    const response = await axios.post('/api/upload-avatar', formData, {
      
    });

    avatarUrl.value = response.data.avatarUrl; 
    sessionStorage.setItem('avatarUrl', avatarUrl.value);
    alert("大頭貼上傳成功！");
  } catch (error) {
    console.error("上傳失敗:", error);
  }
};

const fetchUserData = async () => {
  const token = localStorage.getItem("token");
  if (!token) {
    router.push('/');
    return;
  }

  username.value = sessionStorage.getItem('username');
  const storedLoginTime = sessionStorage.getItem('lastLogin');
  const storedLoginCount = sessionStorage.getItem('loginCount');
  role.value = sessionStorage.getItem('role') || 'user';

  lastLogin.value = storedLoginTime ? new Date(storedLoginTime).toLocaleString() : "無登入記錄";
  loginCount.value = storedLoginCount ? parseInt(storedLoginCount, 10) : 0;

  console.log("存儲在 sessionStorage 的角色:", sessionStorage.getItem('role'));

  try {
    const response = await axios.get('/api/users', {
      withCredentials: true
    });



    users.value = response.data;   
    
    for (let i = 0; i < users.value.length; i++) {
      users.value[i].last_login = users.value[i].last_login ? new Date(users.value[i].last_login).toLocaleString() : "無登入記錄";
      users.value[i].login_count = users.value[i].login_count ? parseInt(users.value[i].login_count, 10) : 0;
    }

    if (role.value === 'admin') {
      console.log("Admin 使用者資料:", users.value);
    } else {
      console.log("普通使用者資料:", users.value);
    }
  } catch (error) {
    console.error("獲取用戶資料失敗:", error);
  }
};

onMounted(fetchUserData);

defineExpose({
  logout
});
</script>

<style>
body, html {
  height: 100%;
  margin: 0;
  background: linear-gradient(135deg, #ea669d, #fceb05);
  overflow-x: hidden;
}

.dash-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh; 
  max-width: 900px; 
  margin: 0 auto;
  padding: 20px;
  box-sizing: border-box;
  position: relative;
  z-index: 1;
}

.dash-table {
  width: 100%; 
  max-height: 400px; 
  overflow-y: auto; 
  border-collapse: collapse;
  margin-bottom: 10px;
  font-size: larger;
  text-align: left;
  background-color: white; 
  border-radius: 5px; 
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); 
}

.dash-table th,
.dash-table td {
  padding: 12px;
  border: 1px solid #ccc;
}

.dash-table th {
  background-color: #f0f0f0;
  position: sticky;
  top: 0; 
  z-index: 1;
}

button {
  padding: 10px 20px;
  font-size: 16px;
  cursor: pointer;
  background-color: #f0a500;
  border: none;
  border-radius: 5px;
  color: white;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); 

}

button:hover {
  background-color: #e88f00;
}

.avatar-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 20px;
}

.avatar-preview {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  object-fit: cover;
  margin-bottom: 10px;
  border: 2px solid #f0a500;
}

input[type="file"] {
  margin-bottom: 10px;
}

</style>
