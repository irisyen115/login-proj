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
	filePath := fmt.Sprintf("%s/%d.jpg", uploadFolder, userID)

	if _, err := os.Stat(filePath); err == nil {
		return filePath, nil
	}

	resp, err := http.Get(imageURL)
	if err != nil {
		return "", fmt.Errorf("failed to download image: %v", err)
	}
	if resp.StatusCode != http.StatusOK {
		return "", fmt.Errorf("failed to download image, status: %s", resp.Status)
	}

	defer resp.Body.Close()

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
		user.Email = email

		if err := db.Create(&user).Error; err != nil {
			return nil, fmt.Errorf("創建用戶失敗: %v", err)
		}
	}

	if picture != "" {
		filepath, err := downloadProfileImage(picture, user.ID, utils.Cfg.UploadFolder)
		if err != nil {
			return nil, fmt.Errorf("下載圖片失敗: %v", err)
		}

		user.PictureName = fmt.Sprintf("%d.jpg", user.ID)
		user.ProfileImage = filepath
	}

	user.LastLogin = models.CustomTime(time.Now())
	utils.UpdateLoginCacheState(user.ID, db)

	if err := db.Save(&user).Error; err != nil {
		return nil, fmt.Errorf("保存用戶資料失敗: %v", err)
	}

	return &user, nil
}

func IdentifyGoogleUserByToken(db *gorm.DB, googleToken string, username string, password string) (*models.User, error) {
	var user models.User

	switch {
	case googleToken != "":
		googleUserInfo, err := verifyGoogleToken(googleToken, utils.Cfg.GoogleClientID)
		if err != nil {
			return nil, fmt.Errorf("google verification failed: %v", err)
		}
		if googleUserInfo.Email == "" {
			return nil, fmt.Errorf("google 資料中無 email")
		}
		if err := db.Where("email = ?", googleUserInfo.Email).First(&user).Error; err != nil {
			return nil, fmt.Errorf("找不到使用者: %s", googleUserInfo.Email)
		}
	case username != "" && password != "":
		if err := db.Where("username = ?", username).First(&user).Error; err != nil {
			return nil, fmt.Errorf("找不到使用者: %s", username)
		}
		if user.PasswordHash == "" || !user.CheckPassword(password) {
			return nil, fmt.Errorf("密碼錯誤: %s", username)
		}
	default:
		return nil, fmt.Errorf("請提供 Google Token 或帳密登入資訊")
	}

	return &user, nil
}

func verifyGoogleToken(googleToken string, clientID string) (*GoogleUserInfo, error) {
	ctx := context.Background()
	tokenInfo, err := idtoken.Validate(ctx, googleToken, clientID)
	if exp, ok := tokenInfo.Claims["exp"].(float64); ok {
		if int64(exp) < time.Now().Unix() {
			return nil, errors.New("token 已過期")
		}
	}

	if err != nil {
		log.Printf("Google Token 驗證失敗: %v", err)
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
		c.JSON(http.StatusBadRequest, gin.H{"error": fmt.Sprintf("已綁定 %s 信箱", user.Email)})
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
	_, err := utils.TriggerEmail(fmt.Sprintf("%s/send-mail", utils.Cfg.IrisDSURL), user.Email, subject, bodyStr)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "email 發送失敗"})
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
