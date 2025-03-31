<template>
    <nav class="navbar">
        <ul class="navbar-list">
          <li style="font-size: larger;justify-content: center;color:lightgray;">用戶: {{ username }}</li>
          <li><button @click="logout" class="navbar-item logout-btn">登出</button></li>
        </ul>
        <div class="profileImage">
            <img v-if="profileImage" :src="profileImage" alt="使用者頭像" class="profile-image" />
            <div v-else class="default-avatar">無頭像</div>
        </div>
    </nav>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import { eventBus } from '../utils/eventBus';

const router = useRouter();

const logout = () => {
  localStorage.removeItem('token');
  sessionStorage.clear();
  router.push('/');
};

const profileImage = ref('');
const username = ref(sessionStorage.getItem('username'));
const fetchUserImage = async () => {
try {
  const response = await axios.get('/api/get_user_image', { responseType: 'blob', withCredentials: true });
  console.log("API 回傳的資料:", response);

  if (response.status === 200) {
      const imageUrl = URL.createObjectURL(response.data);
      profileImage.value = imageUrl;
    }
  } catch (error) {
    console.error('取得用戶圖片失敗:', error);
    profileImage.value = '';
  }
};

eventBus.on('avatarUpdated', fetchUserImage);

onMounted(fetchUserImage);
</script>

<style scoped>
.navbar {
    background-color: #863535;
    padding: 10px 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.navbar-list {
    list-style-type: none;
    margin: 0;
    padding: 0;
    display: flex;
    justify-content: space-around;
    width: 70%;
}

.navbar-item {
    color: white;
    text-decoration: none;
    font-size: 18px;
    padding: 10px;
}

.navbar-item:hover {
    background-color: #575757;
    border-radius: 5px;
}

.logout-btn {
    background-color: #f44336;
    border: none;
    color: white;
    cursor: pointer;
}

.logout-btn:hover {
    background-color: #e53935;
}

.profile-image {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  margin-right: 10px;
}

.default-avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background-color: #bbb;
    display: flex;
    justify-content: center;
    align-items: center;
    color: white;
}
</style>
