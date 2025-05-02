package controllers

import (
	"net/http"
	"strconv"

	"golang-app/models"
	"golang-app/services"

	"github.com/gin-gonic/gin"
)

func RegisterUserRoutes(r *gin.Engine) {
	r.GET("/users", GetUsers)
}

func GetUsers(c *gin.Context) {
	userIDValue, exists := c.Get("user_id")
	if !exists {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "未登入"})
		return
	}

	userIDStr, ok := userIDValue.(string)
	if !ok {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "使用者 ID 轉換錯誤"})
		return
	}

	userID64, err := strconv.ParseUint(userIDStr, 10, 32)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "無效的 user_id"})
		return
	}
	userID := uint(userID64)

	userData, err := services.FetchUsersData(userID, models.DB)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, userData)
}
