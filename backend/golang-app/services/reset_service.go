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
			fmt.Println("使用者不存在")
		} else {
			fmt.Println("查詢時發生錯誤:", result.Error)
		}

		if time.Now().After(passwordVerify.ValidUntil) {
			return "", "驗證密鑰已過期"
		}

		var user models.User
		result := db.Where("passwordVerify.UserID = ?", passwordVerify.UserID).First(&user)
		if result.Error != nil {
			if errors.Is(result.Error, gorm.ErrRecordNotFound) {
				fmt.Println("使用者不存在")
			} else {
				fmt.Println("查詢時發生錯誤:", result.Error)
			}

			user.PasswordHash = newPassword
			if err := db.Save(&user).Error; err != nil {
				return "", fmt.Sprintf("發生錯誤: %v", err)
			}

			return "密碼重設成功，請重新登入", ""
		}
	}
	return "", "發生錯誤"
}
