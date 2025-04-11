package services

import (
	"errors"
	"golang-app/models"
	"golang-app/utils"
	"time"

	"github.com/go-redis/redis/v8"
	"golang.org/x/net/context"
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

func RegisterUser(data RegisterRequest) (map[string]interface{}, error) {
	if data.Username == "" || data.Password == "" || data.Email == "" {
		return nil, errors.New("請提供帳號、密碼和電子郵件")
	}

	var existingUser models.User
	if err := utils.Db.Where("email = ?", data.Email).First(&existingUser).Error; err == nil {
		return nil, errors.New("帳號已存在")
	}

	newUser := models.User{
		Username:     data.Username,
		Email:        &data.Email,
		PasswordHash: data.Password,
	}

	if err := utils.Db.Create(&newUser).Error; err != nil {
		return nil, err
	}

	return map[string]interface{}{"user": newUser, "role": "user"}, nil
}

func LoginUser(data LoginRequest) (map[string]interface{}, error) {

	if data.Username == "" || data.Password == "" {
		return nil, errors.New("請提供帳號和密碼")
	}

	var user models.User
	if err := utils.Db.Where("username = ?", data.Username).First(&user).Error; err != nil {
		return nil, errors.New("帳號或密碼錯誤")
	}

	if user.PasswordHash != data.Password {
		return nil, errors.New("帳號或密碼錯誤")
	}

	*user.LastLogin = time.Now()
	user.LoginCount++
	if err := utils.Db.Save(&user).Error; err != nil {
		return nil, err
	}

	utils.UpdateLoginCacheState(user.ID)

	return map[string]interface{}{
		"user_id":     user.ID,
		"role":        user.Role,
		"last_login":  user.LastLogin,
		"login_count": user.LoginCount,
	}, nil
}

func GetUserByID(uid uint) (*models.User, error) {
	if uid == 0 {
		return nil, nil
	}

	cachedUserData, err := utils.RedisClient.Get(context.Background(), utils.UserKey(uid)).Result()
	if err != nil && err != redis.Nil {
		return nil, err
	}
	if cachedUserData != "" {
		return models.UserFromJSON(cachedUserData)
	}

	var user models.User
	if err := utils.Db.First(&user, uid).Error; err != nil {
		return nil, nil
	}

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
func FetchUsersData(userID uint) (interface{}, error) {
	user, err := GetUserByID(userID)
	if err != nil {
		return nil, err
	}

	if user.Role == "admin" {
		var users []models.User
		if err := utils.Db.Select("id", "username", "last_login", "login_count", "role").Find(&users).Error; err != nil {
			return nil, err
		}
		return users, nil
	} else if user.Role == "user" {
		return []models.User{*user}, nil
	}

	return nil, errors.New("未知的角色")
}
