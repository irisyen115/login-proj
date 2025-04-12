package controllers

import (
	"net/http"

	"golang-app/services"
	"golang-app/utils"

	"github.com/gin-gonic/gin"
)

func RegisterResetRoutes(r *gin.Engine) {
	reset := r.Group("/reset")
	{
		reset.POST("/reset-password/:password_verify_code", ResetPassword)
	}
	r.POST("/reset-password/:password_verify_code", ResetPassword)
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

	result, err := services.ResetUserPassword(verifyCode, json.Password, utils.Db)
	if err != "" {
		c.JSON(http.StatusBadRequest, gin.H{"message": err})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": result})
}
