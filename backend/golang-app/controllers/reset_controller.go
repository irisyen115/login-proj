package controllers

import (
	"net/http"

	"golang-app/services"

	"github.com/gin-gonic/gin"
)

func RegisterResetRoutes(r *gin.Engine) {
	reset := r.Group("/reset")
	{
		reset.POST("/reset-password/:password_verify_code", ResetPassword)
	}
}

func ResetPassword(c *gin.Context) {
	verifyCode := c.Param("password_verify_code")

	var json struct {
		Password string `json:"password"`
	}
	if err := c.ShouldBindJSON(&json); err != nil || json.Password == "" {
		c.JSON(http.StatusBadRequest, gin.H{"message": "請提供新密碼"})
		return
	}

	result, err := services.ResetUserPassword(verifyCode, json.Password)
	if err != "" {
		c.JSON(http.StatusBadRequest, gin.H{"message": err})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": result})
}

func ResetHandler(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"message": "密碼已重設",
	})
}

func ResetHandlerHTTP(w http.ResponseWriter, r *http.Request) {
	c, _ := gin.CreateTestContext(w)
	c.Request = r

	ResetHandler(c)
}
