package services

import (
	"errors"
	"fmt"
	"golang-app/models"
	"time"

	_ "github.com/jinzhu/gorm/dialects/sqlite"
	"gorm.io/gorm"
)

func ResetUserPassword(passwordVerifyCode, newPassword string, db *gorm.DB) (string, string) {
	var passwordVerify models.PasswordVerify
	result := db.Where("password_verify_code = ?", passwordVerifyCode).First(&passwordVerify)

	if result.Error != nil {
		if errors.Is(result.Error, gorm.ErrRecordNotFound) {
			return "", "無效的驗證碼"
		}
		return "", fmt.Sprintf("查詢驗證碼時發生錯誤: %v", result.Error)
	}

	if time.Now().After(passwordVerify.ValidUntil) {
		return "", "驗證密鑰已過期"
	}

	var user models.User
	result = db.First(&user, passwordVerify.UserID)
	if result.Error != nil {
		if errors.Is(result.Error, gorm.ErrRecordNotFound) {
			return "", "找不到對應的使用者"
		}
		return "", fmt.Sprintf("查詢使用者時發生錯誤: %v", result.Error)
	}

	user.SetPassword(newPassword)
	if err := db.Save(&user).Error; err != nil {
		return "", fmt.Sprintf("更新密碼時發生錯誤: %v", err)
	}

	return "密碼重設成功，請重新登入", ""
}
