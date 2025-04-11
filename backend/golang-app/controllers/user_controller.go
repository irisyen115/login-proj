package controllers

import (
	"net/http"

	"golang-app/services"

	"github.com/gin-gonic/gin"
)

func RegisterUserRoutes(r *gin.Engine) {
	userGroup := r.Group("/users")
	{
		userGroup.GET("", GetUsers)
	}
}

func GetUsers(c *gin.Context) {
	userID, exists := c.Get("user_id")
	if !exists {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "未授權"})
		return
	}

	userData, err := services.FetchUsersData(userID.(uint))
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": err})
		return
	}

	c.JSON(http.StatusOK, userData)
}

func UserHandler(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"message": "用戶資料處理成功",
	})
}

func UserHandlerHTTP(w http.ResponseWriter, r *http.Request) {
	c, _ := gin.CreateTestContext(w)
	c.Request = r

	UserHandler(c)
}
