package controllers

import (
	"net/http"
	"os"
	"path/filepath"

	"golang-app/services"
	"golang-app/utils"

	"github.com/gin-gonic/gin"
	"gorm.io/gorm"
)

func RegisterFileRoutes(r *gin.Engine) {
	file := r.Group("/file")
	{
		file.POST("/upload-avatar", UploadAvatar)
		file.GET("/get_user_image", GetUserImage)
	}
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
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "請提供照片"})
		return
	}
	db := c.MustGet("db").(*gorm.DB)
	avatarURL, err := services.SaveUserAvatar(db, userID.(uint), file)

	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "照片上傳錯誤: " + err.Error()})
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

	user, err := services.GetUserByID(uid, utils.Db)
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

	c.FileAttachment(fullPath, pictureName)
}
