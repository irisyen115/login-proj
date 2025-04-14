package controllers

import (
	"net/http"

	"golang-app/models"
	"golang-app/services"

	"github.com/gin-gonic/gin"
)

func RegisterEmailRoutes(r *gin.Engine) {
	r.POST("/send-authentication", SendAuthentication)
	r.POST("/verify-email", VerifyEmail)
	r.POST("/verify-code", VerifyCode)
	r.POST("/request-bind-email", RequestRebindEmail)
}

func SendAuthentication(c *gin.Context) {
	var req struct {
		Username string `json:"username"`
	}

	if err := c.ShouldBindJSON(&req); err != nil || req.Username == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "請輸入用戶名"})
		return
	}

	result := services.SendAuthenticationEmail(req.Username, models.DB)
	c.JSON(http.StatusOK, result)
}

func VerifyEmail(c *gin.Context) {
	var req struct {
		Username string `json:"username"`
	}

	if err := c.ShouldBindJSON(&req); err != nil || req.Username == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "請輸入用戶名"})
		return
	}

	result := services.SendEmailVerification(req.Username, models.DB)
	if errMsg, ok := result["error"]; ok {
		c.JSON(http.StatusBadRequest, gin.H{"error": errMsg})
		return
	}

	c.JSON(http.StatusOK, result)
}

func VerifyCode(c *gin.Context) {
	var req struct {
		Username         string `json:"username"`
		VerificationCode string `json:"verificationCode"`
	}

	if err := c.ShouldBindJSON(&req); err != nil || req.Username == "" || req.VerificationCode == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "缺少用戶名或驗證碼"})
		return
	}

	result := services.SendEmailCode(req.Username, models.DB, req.VerificationCode)
	if errMsg, ok := result["error"]; ok {
		c.JSON(http.StatusBadRequest, gin.H{"error": errMsg})
		return
	}

	c.JSON(http.StatusOK, result)
}

func RequestRebindEmail(c *gin.Context) {
	var req struct {
		Username string `json:"username"`
	}

	if err := c.ShouldBindJSON(&req); err != nil || req.Username == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "缺少 username"})
		return
	}

	result, err := services.SendRebindRequestEmail(req.Username, models.DB)
	if err != 200 {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "寄信失敗", "detail": err})
		return
	}

	c.JSON(http.StatusOK, result)
}
