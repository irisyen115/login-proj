<template>
  <div>
    <h2 v-if="isLoading">正在載入上傳紀錄...</h2>
    <h2 v-else-if="batches.length > 0">
      {{ batches[0].name }} 📦 上傳紀錄 {{ formatDate(batches[0].upload_time) }}
    </h2>
    <h2 v-else>沒有任何上傳紀錄</h2>

    <div v-for="batch in batches" :key="batch.id" class="batch">
      <h3>批次 {{ batch.batch_number }} - {{ formatDate(batch.upload_time) }}</h3>
      <p>上傳張數：{{ batch.num_photos }}</p>
      <p>上傳人物：{{ batch.upload_person }}</p>
      <hr />
    </div>
  </div>
</template>


<script>
import axios from 'axios';

export default {
  name: 'UploadBatches',
  data() {
    return {
      batches: [],
      isLoading: true
    };
  },
  methods: {
  async handleUploadComplete() {
    await this.fetchUploadBatches();
  },

  async fetchUploadBatches() {
    this.isLoading = true;
    try {
      const response = await axios.get('/api/upload/upload_batches', { withCredentials: true });
      this.batches = response.data;
    } catch (error) {
      console.error('取得上傳紀錄失敗：', error);
    } finally {
      this.isLoading = false;
    }
    },
    formatDate(dateStr) {
      const date = new Date(dateStr);
      return date.toLocaleString();
    }
  },
  mounted() {
    this.fetchUploadBatches();
  }
};
</script>

<style scoped>
.batch {
  margin-bottom: 1.5rem;
  text-align: center;
}

h2, h3, p {
  text-align: center;
}
.photos {
  display: flex;
  flex-wrap: wrap;
}
.photo-item {
  margin-right: 1rem;
  text-align: center;
}
</style>