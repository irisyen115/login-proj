package controllers

import (
	"net/http"

	"golang-app/services"

	"golang-app/utils"

	"github.com/gin-gonic/gin"
)

func RegisterUserRoutes(r *gin.Engine) {
	userGroup := r.Group("/users")
	{
		userGroup.GET("", GetUsers)
	}
	r.GET("", GetUsers)
}

func GetUsers(c *gin.Context) {
	userID, exists := c.Get("user_id")
	if !exists {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "未授權"})
		return
	}

	userData, err := services.FetchUsersData(userID.(uint), utils.Db)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": err})
		return
	}

	c.JSON(http.StatusOK, userData)
}
