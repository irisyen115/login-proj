package controllers

import (
	"log"
	"net/http"

	"golang-app/services"

	"golang-app/utils"

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

	uid, ok := userID.(uint)
	if !ok {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "使用者 ID 無效"})
		return
	}

	log.Printf("utils.Db is nil? %v", utils.Db == nil)
	userData, err := services.FetchUsersData(uid, utils.Db)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, userData)
}
