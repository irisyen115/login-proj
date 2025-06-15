<template>
  <div class="photo-list">
    <div v-if="isLoading" class="loading-overlay">
      <div class="loading-spinner"></div>
    </div>

    <h1>{{ userName }}的照片列表</h1>

    <!-- 新增切換按鈕 -->
    <div style="display: flex; justify-content: center; margin-bottom: 16px;">
      <button
        :class="{ active: viewMode === 'upload' }"
        @click="viewMode = 'upload'"
        style="margin-right: 12px;"
      >上傳照片</button>

      <button
        :class="{ active: viewMode === 'blacklist' }"
        @click="viewMode = 'blacklist'"
      >黑名單照片</button>
    </div>

    <!-- 依照 viewMode 決定要顯示哪個區塊 -->

    <!-- 上傳照片列表 -->
    <form v-if="viewMode === 'upload'">
      <div class="image-grid">
        <div
          v-for="record in uploadRecords"
          :key="record.photo_id"
          class="image-item"
          @click="toggleSelection(record.photo_id)"
          :class="{ selected: selected.some(item => String(item.photo_id) === String(record.photo_id)) }"
        >
          <img
            v-lazy="imageUrl(record)"
            alt="圖片"
          />
          <small v-if="isBlacklisted(record.photo_id)">🚫 黑名單</small>
          <button type="button" @click="handleAddToBlacklist($event, record.photo_id)"
            :disabled="blacklistingPhotoId === record.photo_id">
            <span v-if="blacklistingPhotoId === record.photo_id">處理中...</span>
            <span v-else>加入黑名單</span>
          </button>
        </div>
      </div>
      <div style="display: flex; align-items: center; justify-content: center; margin-top: 12px;">
        <button type="button" @click="deleteSelected" :disabled="isDeleting">
          <span v-if="isDeleting">刪除中...</span>
          <span v-else>刪除所選</span>
        </button>
      </div>
      <div style="margin-top: 12px; text-align: center;">
      </div>
    </form>

    <!-- 黑名單照片列表 -->
    <div v-else-if="viewMode === 'blacklist'">
      <h2>黑名單照片</h2>
      <div class="image-grid">
        <div
          v-for="blackPhoto in blacklist"
          :key="blackPhoto.photo_id"
          class="image-item blacklisted"
        >
          <!-- 找到黑名單照片的詳細資訊來顯示圖片 -->
          <img
            :src="getBlacklistedPhotoUrl(blackPhoto.photo_id)"
            alt="黑名單照片"
          />
        </div>
      </div>
    </div>

  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      uploadRecords: [],
      selected: [],
      blacklist: [],
      isDeleting: false,
      blacklistingPhotoId: null,
      userName: "",
      isLoading: true,
      viewMode: 'upload',
    };
  },
  methods: {
    imageUrl(record) {
      return record.url + '/' + encodeURIComponent(record.filename);
    },
    getBlacklistedPhotoUrl(photoId) {
      const normalizedPhotoId = String(photoId).trim();
      // const arr = Array.from(this.blacklist);
      // const record = arr.find(r => String(r.photo_id).trim() === normalizedPhotoId);
      // const blacklist = [
      //   { photo_id: '283364', url: 'https://irisyen115.synology.me/downloaded_albums', filename: 'IMG_20250309_133025.jpg' },
      //   { photo_id: '284544', url: 'https://irisyen115.synology.me/downloaded_albums', filename: 'IMG_20250315_222901.jpg' },
      // ];

      // const photoId = '283364';
      // const normalizedPhotoId = photoId.trim();

      const record = this.blacklist.find(r => r.photo_id.trim() === normalizedPhotoId);

      console.log(record);

      const img_black = record ? `${record.url}/${record.filename}` : '';
      console.log(img_black)
      return img_black;
    },
    handleAddToBlacklist(event, photoId) {
      event.stopPropagation();
      this.addToBlacklist(photoId);
    },

    async fetchUploadRecords() {
      try {
        const response = await axios.get('/api/upload/upload_records', { withCredentials: true });
        this.uploadRecords = response.data.map(r => ({
          ...r,
          photo_id: String(r.photo_id).trim()
        }));

        if (this.uploadRecords.length > 0) {
          this.userName = this.uploadRecords[0].name;
        }


        console.log('uploadRecords:', this.uploadRecords);
      } catch (error) {
        console.error("獲取上傳紀錄失敗:", error);
      }
    },
    async fetchBlacklist() {
      try {
        const response = await axios.get('/api/upload/blacklist', { withCredentials: true });
        // fetchBlacklist() 中
        this.blacklist = response.data.map(item => ({
          photo_id: String(item.photo_id).trim(),
          url: item.url,           // 從 API 取得完整資料
          filename: item.filename, // 同上
        }));



        console.log('blacklist:', this.blacklist);
      } catch (error) {
        console.error("獲取黑名單失敗:", error);
      }
    },

    isBlacklisted(photoId) {
      const normalizedId = String(photoId).trim();
      return this.blacklist.some(item => String(item.photo_id).trim() === normalizedId);
    },
    toggleSelection(photoId) {
      if (this.isBlacklisted(photoId)) {
        alert(`此圖片 ${photoId} 已被封鎖，無法選取`);
        return;
      }
      const index = this.selected.findIndex(item => String(item.photo_id) === String(photoId));
      if (index === -1) {
        const record = this.uploadRecords.find(r => r.photo_id === photoId);
        if (record) {
          this.selected.push({ photo_id: record.photo_id, filename: record.filename });
        }
      } else {
        this.selected.splice(index, 1);
      }
    },
    async deleteSelected() {
      if (this.selected.length === 0) {
        alert("請選擇要刪除的圖片");
        return;
      }

      if (!confirm("確定要刪除所選圖片嗎？")) return;

      this.isDeleting = true;
      try {
        const response = await fetch('/api/upload/delete_photo', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          },
          credentials: 'include',
          body: JSON.stringify({
            filenames: this.selected.map(item => item.filename),
            person_id: 22492,
            album_name: "default"
          })
        });

        if (!response.ok) {
          const errorText = await response.text();
          console.error("伺服器錯誤：", response.status, errorText);
          alert("刪除失敗（伺服器錯誤）");
          return;
        }

        const data = await response.json();
        if (Array.isArray(data.photo_ids)) {
          alert("刪除成功：" + data.photo_ids.join(", "));
        } else if (data.message) {
          alert(data.message);
        } else {
          alert("刪除成功");
        }

        this.selected = [];
        await this.fetchUploadRecords();
      } catch (error) {
        console.error("刪除圖片失敗:", error);
        alert("刪除失敗，請稍後再試");
      }
    },
    async addToBlacklist(photoId) {
      this.blacklistingPhotoId = photoId;

      try {
        console.log('addToBlacklist called with photoId:', photoId);

        const blacklistRes = await fetch('/api/upload/blacklist_photo', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({
            photo_id: String(photoId),
            reason: "不想再看到這張"
          })
        });
        console.log('blacklistRes.ok:', blacklistRes.ok);

        if (!blacklistRes.ok) {
          const errText = await blacklistRes.text();
          console.error("加入黑名單失敗:", errText);
          throw new Error('加入黑名單失敗');
        }

        const record = this.uploadRecords.find(r => r.photo_id === photoId);
        if (record) {
          const deleteRes = await fetch('/api/upload/delete_photo', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Accept': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify({
              filenames: [record.filename],
              person_id: 22492,
              album_name: "default"
            })
          });
          console.log('deleteRes.ok:', deleteRes.ok);
          if (!deleteRes.ok) throw new Error('刪除圖片失敗');
        }

        await this.fetchBlacklist();
        await this.fetchUploadRecords();
      } catch (error) {
        console.error("加入黑名單或刪除失敗:", error);
        alert("操作失敗");
      }
    },
    async handleUpload(event) {
      const file = event.target.files[0];
      if (!file) return;

      const photo_id = file.name.split('.')[0];
      if (this.isBlacklisted(photo_id)) {
        alert(`此 photo_id ${photo_id} 已被封鎖，無法上傳`);
        return;
      }


      const formData = new FormData();
      formData.append('file', file);
      formData.append('photo_id', photo_id);

      try {
        const res = await fetch('/api/upload/upload_photo', {
          method: 'POST',
          body: formData,
          credentials: 'include',
        });

        const data = await res.json();
        alert(data.message || "上傳成功！");
        await this.fetchUploadRecords();
      } catch (error) {
        console.error("上傳失敗:", error);
        alert("上傳失敗，請稍後再試");
      }
    }
  },
  async mounted() {
    this.isLoading = true;
    await Promise.all([this.fetchUploadRecords(), this.fetchBlacklist()]);
    this.isLoading = false;
  }

};
</script>

<style scoped>
button.active {
  background-color: #3498db;
  color: white;
  border-radius: 6px;
}

.loading-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(255, 255, 255, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}

/* 簡單旋轉動畫 spinner */
.loading-spinner {
  border: 8px solid #f3f3f3; /* 淺灰 */
  border-top: 8px solid #3498db; /* 藍色 */
  border-radius: 50%;
  width: 60px;
  height: 60px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

body, html {
  height: 100%;
  margin: 0;
  background: linear-gradient(135deg, #ff006a, #e7fc05);
  overflow-x: hidden;
}

h1 {
  display: flex;
  align-items: center;
  justify-content: center;
}

.image-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 16px;
  justify-items: center; /* 水平置中每個 image-item */
  align-items: center;
}

.image-item {
  cursor: pointer;
  border: 4px solid #ccc; /* 相框 */
  border-radius: 12px;
  padding: 8px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
  background-color: #fff;
  transition: border-color 0.2s ease, background-color 0.2s ease;
  width: 150px;
  text-align: center;
}

.image-item img {
  display: block;   /* 避免 img 預設的 inline-gap */
  width: 150px;     /* 你想要的圖片寬度 */
  height: auto;
}

.image-item.selected {
  box-shadow: 0 0 0 3px blue;
  border-radius: 6px;
  transition: box-shadow 0.2s ease;
}


.image-item p {
  margin-top: 6px;
  font-size: 14px;
  color: #333;
}

.image-item.blacklisted {
  opacity: 0.5;
  pointer-events: none;
  box-shadow: 0 0 0 2px red;
}

button[disabled] {
  opacity: 0.6;
  pointer-events: none;
  cursor: not-allowed;
}

</style>
