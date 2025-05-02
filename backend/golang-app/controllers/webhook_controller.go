package controllers

import (
	"fmt"
	"golang-app/services"
	"net/http"

	"github.com/gin-gonic/gin"
)

type GoogleBindRequest struct {
	GoogleToken string `json:"google_token"`
	UID         string `json:"uid"`
}

type EmailBindRequest struct {
	Username string `json:"username"`
	Password string `json:"password"`
	UID      string `json:"uid"`
}

func RegisterWebhookRoutes(r *gin.Engine) {
	r.POST("/webhook", webhookHandler)

	r.POST("/bind-google-email", bindGoogleEmail)
	r.POST("/bind-email", bindEmail)
}

func webhookHandler(c *gin.Context) {
	services.HandleWebhookEvent(c)
}

func bindGoogleEmail(c *gin.Context) {
	var req GoogleBindRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "no data"})
		return
	}
	fmt.Printf("👉 收到請求：google_token=%s, uid=%s\n", req.GoogleToken, req.UID)

	if req.GoogleToken == "" || req.UID == "" {
		if req.GoogleToken == "" {
			c.JSON(http.StatusBadRequest, gin.H{"error": "缺少必要的資料(google_token)"})
		} else {
			c.JSON(http.StatusBadRequest, gin.H{"error": "缺少必要的資料(uid)"})
		}
		return
	}

	user, err := services.IdentifyGoogleUserByToken(c, req.GoogleToken, "", "")
	if err != nil || user == nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "登入驗證失敗"})
		return
	}

	services.BindLineUIDToUserEmail(c, req.UID, user)

}

func bindEmail(c *gin.Context) {
	var req EmailBindRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "no data"})
		return
	}

	for _, field := range []struct {
		key string
		val string
	}{
		{"username", req.Username},
		{"password", req.Password},
		{"uid", req.UID},
	} {
		if field.val == "" {
			c.JSON(http.StatusBadRequest, gin.H{"error": fmt.Sprintf("缺少必要的資料(%s)", field.key)})
			return
		}
	}

	user, err := services.IdentifyGoogleUserByToken(c, "", req.Username, req.Password)

	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": fmt.Sprintf("伺服器錯誤: %v", err)})
		return
	}

	services.BindLineUIDToUserEmail(c, req.UID, user)
}
