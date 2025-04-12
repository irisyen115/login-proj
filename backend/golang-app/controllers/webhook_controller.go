package controllers

import (
	"net/http"

	"golang-app/services"

	"github.com/gin-gonic/gin"
	"gorm.io/gorm"
)

type BindGoogleEmailRequest struct {
	GoogleToken string `json:"google_token"`
	Uid         string `json:"uid"`
}

type BindEmailRequest struct {
	Username string `json:"username"`
	Password string `json:"password"`
	Uid      string `json:"uid"`
}

func RegisterWebhookRoutes(r *gin.Engine) {
	webhookGroup := r.Group("/webhook")
	{
		webhookGroup.POST("/bind-google-email", BindGoogleEmail)
		webhookGroup.POST("/bind-email", BindEmail)
	}
	r.POST("/bind-google-email", BindGoogleEmail)
	r.POST("/bind-email", BindEmail)
}

func BindGoogleEmail(c *gin.Context) {
	var bindGoogleEmailRequest BindGoogleEmailRequest
	if err := c.ShouldBindJSON(&bindGoogleEmailRequest); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input data"})
		return
	}

	if bindGoogleEmailRequest.GoogleToken == "" || bindGoogleEmailRequest.Uid == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Missing required fields (google_token or uid)"})
		return
	}

	db := c.MustGet("db").(*gorm.DB)
	user, err := services.IdentifyGoogleUserByToken(db, bindGoogleEmailRequest.GoogleToken, "", "")
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	services.BindLineUIDToUserEmail(c, db, bindGoogleEmailRequest.Uid, user)

	c.JSON(http.StatusOK, gin.H{"message": "Successfully bound LINE UID to user email"})
}

func BindEmail(c *gin.Context) {
	var data map[string]interface{}
	if err := c.ShouldBindJSON(&data); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input data"})
		return
	}

	for _, key := range []string{"username", "password", "uid"} {
		if _, ok := data[key]; !ok {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Missing required field: " + key})
			return
		}
	}

	db := c.MustGet("db").(*gorm.DB)

	user, err := services.IdentifyGoogleUserByToken(db, "", data["username"].(string), data["password"].(string))

	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	lineUID := data["uid"].(string)
	services.BindLineUIDToUserEmail(c, db, lineUID, user)

	c.JSON(http.StatusOK, gin.H{"message": "Successfully bound LINE UID to user email"})
}
