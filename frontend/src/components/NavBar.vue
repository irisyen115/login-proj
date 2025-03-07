<template>
    <nav class="navbar">
        <ul class="navbar-list">
            <li><button @click="logout" class="navbar-item logout-btn">登出</button></li>
        </ul>
        <div class="profileImage">
            <img v-if="profileImage" :src="`/uploads/${profileImage}`" alt="profileImage" class="profile-image" />
            <div v-else class="default-avatar">無頭像</div>
        </div>
    </nav>
</template>

<script setup>
  import { ref, onMounted } from 'vue';
  import { useRouter } from 'vue-router';
  import axios from 'axios';
  
  const router = useRouter();
  
  const logout = () => {
    localStorage.removeItem('token');
    sessionStorage.clear();
    router.push('/');
  };
  
  const profileImage = ref('');
  const users = ref([]);
  const user = ref([]);

  onMounted(async () => {
    try {
        const response = await axios.get('/api/users');  
        console.log("API 回傳的 data:", response.data);
        users.value = response.data;
        
        if (Array.isArray(users.value) && users.value.length > 0) {  
          user.value = users.value[0];              
          profileImage.value = user.value.profile_image ? `/uploads/${user.value.profile_image}` : null;
          console.log("user 為", user.value); 
        }
    } catch (error) {
        console.error('登入失敗:', error);
    }
});

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
