package services

import (
	"errors"
	"fmt"
	"golang-app/models"
	"golang-app/utils"
	"log"
	"time"

	"github.com/gin-gonic/gin"
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
		Email:        data.Email,
		PasswordHash: data.Password,
		Role:         "user",
	}

	if err := db.Create(&newUser).Error; err != nil {
		return nil, err
	}

	return map[string]interface{}{"user": newUser, "role": "user"}, nil
}

func LoginUser(c *gin.Context, data LoginRequest, db *gorm.DB) (map[string]interface{}, error) {

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

	sessionID := utils.GenerateSignedSessionID(user.ID)
	utils.RedisClient.SetEX(utils.Ctx, sessionID, fmt.Sprintf("%d", user.ID), 30*time.Minute)
	c.SetCookie("session_id", sessionID, 1800, "/", "", false, true)

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
		return nil, fmt.Errorf("無效的 userID: %d", uid)
	}
	if db == nil {
		return nil, fmt.Errorf("DB is nil")
	}

	ctx := context.Background()
	redisKey := utils.UserKey(uid)

	var cachedUserData string
	var err error
	maxRetry := 3

	for i := 0; i < maxRetry; i++ {
		cachedUserData, err = utils.RedisClient.Get(ctx, redisKey).Result()
		if err == nil && cachedUserData != "" {
			break
		}
		if err != nil && err != redis.Nil {
			log.Printf("[Redis] 錯誤 (第 %d 次): %v", i+1, err)
		}
		time.Sleep(50 * time.Millisecond)
	}

	if cachedUserData != "" {
		user, err := models.UserFromJSON(cachedUserData)
		if err == nil {
			user.LastLogin = models.CustomTime(time.Now())
			return user, nil
		}
	}

	log.Printf("[DB] 查詢使用者資料 (userID=%d)", uid)
	var user models.User
	if err := db.First(&user, uid).Error; err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			log.Printf("[DB] 查無使用者 (userID=%d)", uid)
			return nil, gorm.ErrRecordNotFound
		}
		log.Printf("[DB] 查詢錯誤 (userID=%d): %v", uid, err)
		return nil, fmt.Errorf("資料庫查詢錯誤: %v", err)
	}

	user.LastLogin = models.CustomTime(time.Now())

	userData, err := user.ToJSON()
	if err != nil {
		log.Printf("[Cache] 將 user 轉換為 JSON 時發生錯誤 (userID=%d): %v", uid, err)
		return nil, fmt.Errorf("將 user 轉換為 JSON 時發生錯誤: %v", err)
	}

	err = utils.RedisClient.SetEX(ctx, redisKey, userData, 3600*time.Second).Err()
	if err != nil {
		log.Printf("[Cache] 寫入 Redis 失敗 (userID=%d): %v", uid, err)
	} else {
		log.Printf("[Cache] 寫入 Redis 成功 (userID=%d)", uid)
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
		usersData = append(usersData, *user)

	default:
		log.Printf("未知的角色: %s", user.Role)
		return nil, fmt.Errorf("未知的角色: %s", user.Role)
	}

	return usersData, nil
}
