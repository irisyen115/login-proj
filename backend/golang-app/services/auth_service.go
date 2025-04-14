package services

import (
	"errors"
	"fmt"
	"golang-app/models"
	"log"
	"net/http"
	"os"
	"strconv"
	"time"

	"golang-app/utils"

	"golang.org/x/net/context"
	"google.golang.org/api/idtoken"

	"github.com/gin-gonic/gin"
	"google.golang.org/api/oauth2/v2"
	"google.golang.org/api/people/v1"
	"gorm.io/gorm"
)

var (
	GoogleClient  *oauth2.Service
	PeopleService *people.Service
)

type GoogleUserInfo struct {
	Email   string
	Name    string
	Picture string
}

func downloadProfileImage(imageURL string, userID uint, uploadFolder string) (string, error) {
	resp, err := http.Get(imageURL)
	if err != nil {
		return "", fmt.Errorf("failed to download image: %v", err)
	}
	defer resp.Body.Close()

	filePath := fmt.Sprintf("%s/%d.jpg", uploadFolder, userID)

	file, err := os.Create(filePath)
	if err != nil {
		return "", fmt.Errorf("failed to create file: %v", err)
	}
	defer file.Close()

	_, err = file.ReadFrom(resp.Body)
	if err != nil {
		return "", fmt.Errorf("failed to write image to file: %v", err)
	}

	return filePath, nil
}

func AuthenticateGoogleUser(idTokenStr string, db *gorm.DB) (*models.User, error) {
	decoded, err := verifyGoogleToken(idTokenStr, utils.Cfg.GoogleClientID)
	if err != nil {
		return nil, fmt.Errorf("無法驗證 Google ID Token: %v", err)
	}

	email := decoded.Email
	name := decoded.Name
	picture := decoded.Picture
	if email == "" {
		return nil, fmt.Errorf("無法取得使用者的 email")
	}

	var user models.User
	if err := db.Where("email = ?", email).First(&user).Error; err != nil {
		user.Username = name
		user.Email = &email

		if err := db.Create(&user).Error; err != nil {
			return nil, fmt.Errorf("創建用戶失敗: %v", err)
		}
	}

	if picture != "" {
		filepath, err := downloadProfileImage(picture, user.ID, utils.Cfg.UploadFolder)
		if err != nil {
			return nil, fmt.Errorf("下載圖片失敗: %v", err)
		}

		if user.PictureName == nil {
			user.PictureName = new(string)
		}
		*user.PictureName = fmt.Sprintf("%d.jpg", user.ID)

		user.ProfileImage = &filepath
		if err := db.Save(&user).Error; err != nil {
			return nil, fmt.Errorf("保存用戶头像失败: %v", err)
		}
	}

	utils.UpdateLoginCacheState(user.ID, db)

	user.LastLogin = models.CustomTime(time.Now())

	if err := db.Save(&user).Error; err != nil {
		return nil, fmt.Errorf("保存用户登录时间失败: %v", err)
	}

	return &user, nil
}

func IdentifyGoogleUserByToken(db *gorm.DB, googleToken string, username string, password string) (*models.User, error) {
	var user models.User

	if googleToken != "" {
		googleUserInfo, err := verifyGoogleToken(googleToken, utils.Cfg.GoogleClientID)
		if err != nil {
			return nil, fmt.Errorf("Google verification failed: %v", err)
		}

		email := googleUserInfo.Email
		if email == "" {
			return nil, fmt.Errorf("Invalid Google user info: no email found")
		}

		if err := db.Where("email = ?", email).First(&user).Error; err != nil {
			return nil, fmt.Errorf("User not found with email: %s", email)
		}
	} else if username != "" && password != "" {
		if err := db.Where("username = ?", username).First(&user).Error; err != nil {
			return nil, fmt.Errorf("User not found with username: %s", username)
		}

		if !user.CheckPassword(password) {
			return nil, fmt.Errorf("Incorrect password for user: %s", username)
		}
	} else {
		return nil, fmt.Errorf("Either google_token or username and password must be provided")
	}

	return &user, nil
}

func verifyGoogleToken(googleToken string, clientID string) (*GoogleUserInfo, error) {
	ctx := context.Background()
	tokenInfo, err := idtoken.Validate(ctx, googleToken, clientID)
	if err != nil {
		log.Printf("Google Token 验证失败: %v", err)
		return nil, fmt.Errorf("failed to verify google token: %v", err)
	}

	iss := tokenInfo.Issuer
	if iss != "accounts.google.com" && iss != "https://accounts.google.com" {
		log.Printf("Invalid token issuer: %v", iss)
		return nil, fmt.Errorf("invalid token issuer")
	}
	email, ok := tokenInfo.Claims["email"].(string)
	if !ok || email == "" {
		return nil, errors.New("無法取得使用者的 email")
	}
	name, _ := tokenInfo.Claims["name"].(string)
	picture, _ := tokenInfo.Claims["picture"].(string)

	return &GoogleUserInfo{
		Email:   email,
		Name:    name,
		Picture: picture,
	}, nil
}

func BindLineUIDToUserEmail(c *gin.Context, db *gorm.DB, lineUID string, user *models.User) {
	if user == nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "帳號不存在"})
		return
	}

	var binding models.LineBindingUser
	result := db.Where("user_id = ?", user.ID).First(&binding)
	if result.Error != nil && !errors.Is(result.Error, gorm.ErrRecordNotFound) {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "資料庫查詢錯誤"})
		return
	}

	if binding.LineID != "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": fmt.Sprintf("已綁定 %s 信箱", *user.Email)})
		return
	}

	binding = models.LineBindingUser{
		UserID: user.ID,
		LineID: lineUID,
	}
	if err := db.Create(&binding).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "資料寫入錯誤"})
		return
	}

	subject := "帳戶綁定確認"
	bodyStr := "您的 Line 已綁定此 Email！"
	_, err := utils.TriggerEmail(fmt.Sprintf("%s/send-mail", utils.Cfg.IrisDSURL), *user.Email, subject, bodyStr)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Email 發送失敗"})
		return
	}

	c.SetCookie("user_id", strconv.Itoa(int(user.ID)), 3600, "/", "", true, true)

	c.JSON(http.StatusOK, gin.H{
		"message":     "綁定成功，請檢查您的 Email",
		"username":    user.Username,
		"role":        user.Role,
		"last_login":  user.LastLogin,
		"login_count": user.LoginCount,
	})
}
