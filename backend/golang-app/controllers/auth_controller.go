package controllers

import (
	"fmt"
	"golang-app/models"
	"golang-app/services"
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
)

func RegisterAuthRoutes(r *gin.Engine) {
	auth := r.Group("/auth")
	{
		auth.POST("/google/callback", GoogleCallback)
		auth.POST("/register", Register)
		auth.POST("/login", Login)
	}
	r.POST("/login", Login)
	r.POST("/register", Register)
	r.POST("/google-callback", GoogleCallback)
}

func GoogleCallback(c *gin.Context) {
	var data map[string]interface{}
	if err := c.ShouldBindJSON(&data); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid JSON"})
		return
	}

	idTokenFromGoogle, exists := data["id_token"].(string)
	if !exists || idTokenFromGoogle == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "缺少 id_token"})
		return
	}

	user, err := services.AuthenticateGoogleUser(idTokenFromGoogle, models.DB)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": fmt.Sprintf("Google OAuth 處理失敗: %v", err)})
		return
	}

	response := gin.H{
		"message":     "Google 登入成功",
		"username":    user.Username,
		"role":        user.Role,
		"last_login":  user.LastLogin,
		"login_count": user.LoginCount,
	}

	c.SetCookie("user_id", fmt.Sprintf("%d", user.ID), 3600, "/", "", false, true)
	c.SetCookie("role", string(user.Role), 3600, "/", "", false, true)

	c.JSON(http.StatusOK, response)
}

func Register(c *gin.Context) {
	var registerRequest services.RegisterRequest

	if err := c.ShouldBindJSON(&registerRequest); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "請提供註冊資料"})
		return
	}

	registerResponse, err := services.RegisterUser(registerRequest, models.DB)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": fmt.Sprintf("註冊失敗: %v", err)})
		return
	}

	userObj, ok := registerResponse["user"].(*models.User)
	if !ok {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "用戶資料轉換失敗"})
		return
	}

	c.SetCookie("user_id", fmt.Sprintf("%d", userObj.ID), 3600, "/", "", false, true)
	c.SetCookie("role", "user", 3600, "/", "", false, true)

	c.JSON(http.StatusOK, gin.H{
		"message": "註冊成功",
		"user":    userObj.Username,
		"role":    "user",
	})
}

func Login(c *gin.Context) {
	var loginRequest services.LoginRequest

	if err := c.ShouldBindJSON(&loginRequest); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "請提供登入資料"})
		return
	}

	loginResponse, err := services.LoginUser(loginRequest, models.DB)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": fmt.Sprintf("登入失敗: %v", err)})
		return
	}

	userID := fmt.Sprintf("%v", loginResponse["user_id"])
	role, _ := loginResponse["role"].(string)
	lastLogin, _ := loginResponse["last_login"].(time.Time)
	loginCount, _ := loginResponse["login_count"].(int)

	c.SetCookie("user_id", userID, 3600, "/", "", false, true)
	c.SetCookie("role", role, 3600, "/", "", false, true)

	c.JSON(http.StatusOK, gin.H{
		"message":     "登入成功",
		"role":        role,
		"last_login":  lastLogin,
		"login_count": loginCount,
	})
}

func Logout(c *gin.Context) {
	c.SetCookie("user_id", "", -1, "/", "", false, true)
	c.SetCookie("role", "", -1, "/", "", false, true)

	c.JSON(http.StatusOK, gin.H{
		"message": "登出成功",
	})
}
