package services

import (
	"errors"
	"fmt"
	"golang-app/models"
	"golang-app/utils"
	"log"
	"time"

	"github.com/go-redis/redis/v8"
	"golang.org/x/net/context"
	"gorm.io/gorm"
)

type RegisterRequest struct {
	Username string `json:"username"`
	Password string `json:"password"`
	Email    string `json:"email"`
}

type LoginRequest struct {
	Username string `json:"username"`
	Password string `json:"password"`
}

func RegisterUser(data RegisterRequest, db *gorm.DB) (map[string]interface{}, error) {
	if data.Username == "" || data.Password == "" || data.Email == "" {
		return nil, errors.New("請提供帳號、密碼和電子郵件")
	}

	var existingUser models.User
	if err := db.Where("email = ?", data.Email).First(&existingUser).Error; err == nil {
		return nil, errors.New("帳號已存在")
	}

	newUser := models.User{
		Username:     data.Username,
		Email:        &data.Email,
		PasswordHash: data.Password,
		Role:         "user",
	}

	if err := db.Create(&newUser).Error; err != nil {
		return nil, err
	}

	return map[string]interface{}{"user": newUser, "role": "user"}, nil
}

func LoginUser(data LoginRequest, db *gorm.DB) (map[string]interface{}, error) {

	if data.Username == "" || data.Password == "" {
		return nil, errors.New("請提供帳號和密碼")
	}

	var user models.User
	if err := db.Where("username = ?", data.Username).First(&user).Error; err != nil {
		return nil, errors.New("帳號或密碼錯誤")
	}

	if !user.CheckPassword(data.Password) {
		return nil, errors.New("帳號或密碼錯誤")
	}
	user.UpdateLastLogin()

	if err := db.Save(&user).Error; err != nil {
		return nil, err
	}

	if err := utils.UpdateLoginCacheState(user.ID, db); err != nil {
		log.Printf("更新快取失敗: %v", err)
	}

	return map[string]interface{}{
		"user_id":     user.ID,
		"role":        user.Role,
		"last_login":  user.LastLogin,
		"login_count": user.LoginCount,
	}, nil
}

func GetUserByID(uid uint, db *gorm.DB) (*models.User, error) {
	if uid == 0 {
		return nil, nil
	}
	if db == nil {
		return nil, fmt.Errorf("DB is nil")
	}

	cachedUserData, err := utils.RedisClient.Get(context.Background(), utils.UserKey(uid)).Result()
	if err != nil && err != redis.Nil {
		return nil, err
	}
	if cachedUserData != "" {
		return models.UserFromJSON(cachedUserData)
	}

	var user models.User
	if err := db.First(&user, uid).Error; err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return nil, gorm.ErrRecordNotFound
		}
		return nil, err
	}

	user.LastLogin = models.CustomTime(time.Now())
	userData, err := user.ToJSON()
	if err != nil {
		return nil, err
	}

	err = utils.RedisClient.SetEX(context.Background(), utils.UserKey(uid), userData, 3600*time.Second).Err()
	if err != nil {
		return nil, err
	}

	return &user, nil
}

func FetchUsersData(userID uint, db *gorm.DB) (interface{}, error) {
	user, err := GetUserByID(userID, db)
	if err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return nil, errors.New("使用者不存在")
		}
		return nil, fmt.Errorf("取得使用者資料時發生錯誤: %v", err)
	}

	var usersData []models.User

	switch user.Role {
	case "admin":
		if err := db.Select("id, username, last_login, login_count, role").Find(&usersData).Error; err != nil {
			return nil, fmt.Errorf("查詢用戶資料失敗: %v", err)
		}

	case "user":
		for i := range usersData {
			usersData[i].LastLogin = models.CustomTime(time.Now())
		}
		usersData = append(usersData, *user)
	default:
		log.Printf("未知的角色: %s", user.Role)
		return nil, fmt.Errorf("未知的角色: %s", user.Role)
	}

	return usersData, nil
}
