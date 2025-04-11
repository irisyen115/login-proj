package utils

import (
	"bytes"
	"encoding/json"
	"fmt"
	"golang-app/config"
	"log"
	"math/rand"
	"net/http"
	"strings"
	"time"

	"github.com/go-redis/redis/v8"
	"google.golang.org/api/oauth2/v2"
	"gorm.io/gorm"
)

type User struct {
	ID           uint       `gorm:"primaryKey"`
	Username     string     `json:"username"`
	Email        string     `json:"email"`
	ProfileImage string     `json:"profile_image"`
	PictureName  string     `json:"picture_name"`
	LastLogin    *time.Time `json:"last_login"`
	LoginCount   int        `json:"login_count"`
}

var (
	Cfg          config.Config
	RedisClient  *redis.Client
	Db           *gorm.DB
	GoogleClient *oauth2.Service
)

func GenerateResetToken(length int) string {
	const charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
	var token strings.Builder
	for i := 0; i < length; i++ {
		token.WriteByte(charset[rand.Intn(len(charset))])
	}
	return token.String()
}

func UserKey(uid uint) string {
	return fmt.Sprintf("user:%d", uid)
}

func UpdateLoginCacheState(uid uint) {
	userKey := UserKey(uid)
	cached, err := RedisClient.Get(RedisClient.Context(), userKey).Result()
	if err == redis.Nil {
		var user User
		if err := Db.First(&user, uid).Error; err != nil {
			log.Println("Error retrieving user:", err)
			return
		}
		userData, _ := json.Marshal(user)
		RedisClient.Set(RedisClient.Context(), userKey, userData, 1*time.Hour)
	} else if err == nil {
		var userData map[string]interface{}
		if err := json.Unmarshal([]byte(cached), &userData); err != nil {
			log.Println("Error unmarshalling cached data:", err)
			return
		}
		userData["last_login"] = time.Now().UTC().Format(time.RFC3339)
		userData["login_count"] = userData["login_count"].(int) + 1
		RedisClient.Set(RedisClient.Context(), userKey, userData, 1*time.Hour)
	} else {
		log.Println("Redis error:", err)
	}
}

func TriggerEmail(url, recipient, subject, body string) (map[string]interface{}, error) {
	payload := map[string]string{
		"recipient": recipient,
		"subject":   subject,
		"body":      body,
	}

	jsonData, err := json.Marshal(payload)
	if err != nil {
		return nil, err
	}

	resp, err := http.Post(url, "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("email 發送失敗，狀態碼: %d", resp.StatusCode)
	}

	var result map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, err
	}

	return result, nil
}
