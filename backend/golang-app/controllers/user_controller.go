package controllers

import (
	"net/http"

	"golang-app/models"
	"golang-app/services"

	"github.com/gin-gonic/gin"
)

func RegisterUserRoutes(r *gin.Engine) {
	r.GET("/users", GetUsers)
}

func GetUsers(c *gin.Context) {
	userID, exists := c.Get("user_id")
	if !exists {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "未授權"})
		return
	}
	var user models.User
	if err := models.DB.First(&user, userID).Error; err != nil {
		c.JSON(500, gin.H{"error": "找不到用戶"})
		return
	}

	uid, ok := userID.(uint)
	if !ok {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "使用者 ID 無效"})
		return
	}

	userData, err := services.FetchUsersData(uid, models.DB)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, userData)
}
