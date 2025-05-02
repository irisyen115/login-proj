package utils

import (
	"context"
	"crypto/hmac"
	"crypto/sha256"
	"encoding/base64"
	"encoding/hex"
	"fmt"
	"golang-app/models"
	"math/rand"
	"time"
)

var (
	Ctx       = context.Background()
	secretKey = []byte(generateSecret())
)

func generateSecret() string {
	b := make([]byte, 32)
	rand.Read(b)
	return hex.EncodeToString(b)
}

func GenerateSignedSessionID(userID uint) string {
	raw := fmt.Sprintf("%d:%d", userID, time.Now().UnixNano())
	mac := hmac.New(sha256.New, secretKey)
	mac.Write([]byte(raw))
	signature := mac.Sum(nil)
	signed := append([]byte(raw), '.')
	signed = append(signed, signature...)
	return base64.URLEncoding.EncodeToString(signed)
}

func CacheUser(u *models.User) {
	key := fmt.Sprintf("user:%d", u.ID)
	data, err := u.ToJSON()
	if err != nil {
		fmt.Printf("[ERROR] 快取使用者 JSON 失敗: %v\n", err)
		return
	}

	RedisClient.SetEX(Ctx, key, data, time.Hour)
}

func GetCachedUser(id uint) (*models.User, error) {
	key := fmt.Sprintf("user:%d", id)
	data, err := RedisClient.Get(Ctx, key).Result()
	if err != nil {
		return nil, err
	}
	return models.UserFromJSON(data)
}
