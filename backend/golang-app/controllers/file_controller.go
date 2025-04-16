package controllers

import (
	"fmt"
	"net/http"
	"os"
	"path/filepath"

	"golang-app/models"
	"golang-app/services"
	"golang-app/utils"

	"github.com/gin-gonic/gin"
)

func RegisterFileRoutes(r *gin.Engine) {
	r.POST("/upload-avatar", UploadAvatar)
	r.GET("/get_user_image", GetUserImage)
}

func UploadAvatar(c *gin.Context) {
	userID, exists := c.Get("user_id")

	if !exists {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "未授權"})
		return
	}

	file, err := c.FormFile("file")
	if err != nil || file == nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "請提供照片"})
		return
	}

	avatarURL, err := services.SaveUserAvatar(models.DB, userID.(uint), file)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": fmt.Sprintf("照片上傳錯誤: %v", err)})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"message":    "照片上傳成功",
		"avatar_url": avatarURL,
	})
}

func GetUserImage(c *gin.Context) {
	userID, exists := c.Get("user_id")
	if !exists {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "未授權"})
		return
	}

	uid, ok := userID.(uint)
	if !ok {
		c.JSON(http.StatusBadRequest, gin.H{"error": "用戶 ID 格式錯誤"})
		return
	}

	user, err := services.GetUserByID(uid, models.DB)
	if err != nil || user == nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "用戶未找到"})
		return
	}

	pictureName := services.GetUserImageService(user)
	if pictureName == "" {
		c.JSON(http.StatusNotFound, gin.H{"error": "無圖片可顯示"})
		return
	}

	fullPath := filepath.Join(utils.Cfg.UploadFolder, pictureName)
	if _, err := os.Stat(fullPath); os.IsNotExist(err) {
		c.JSON(http.StatusNotFound, gin.H{"error": "圖片不存在於伺服器"})
		return
	}
	c.Header("Cache-Control", "no-cache, no-store, must-revalidate")
	c.Header("Pragma", "no-cache")
	c.Header("Expires", "0")

	c.FileAttachment(fullPath, pictureName)
}
