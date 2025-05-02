package services

import (
	"errors"
	"fmt"
	"golang-app/models"
	"golang-app/utils"
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
	_ "github.com/jinzhu/gorm/dialects/sqlite"
	"gorm.io/gorm"
)

func SendAuthenticationEmail(username string, db *gorm.DB) map[string]interface{} {
	var user models.User
	result := db.Where("username = ?", username).First(&user)

	if result.Error != nil {
		if errors.Is(result.Error, gorm.ErrRecordNotFound) {
			return map[string]interface{}{"error": "使用者不存在"}
		}
		return map[string]interface{}{"error": "資料庫查詢錯誤"}
	}

	if user.Email == "" {
		return map[string]interface{}{"message": "用戶未綁定 Email"}
	}

	var passwordVerify models.PasswordVerify
	db.Where("user_id = ?", user.ID).Order("valid_until desc").First(&passwordVerify)
	currentTime := time.Now()

	if passwordVerify.ID != 0 && currentTime.Before(passwordVerify.ValidUntil) {
		return map[string]interface{}{"message": "驗證碼已發送，請前往電子信箱查看"}
	}

	newPasswordVerify := models.PasswordVerify{
		PasswordVerifyCode: utils.GenerateResetToken(30),
		ValidUntil:         currentTime.Add(15 * time.Minute),
		UserID:             user.ID,
	}
	if err := db.Create(&newPasswordVerify).Error; err != nil {
		return map[string]interface{}{"error": "建立驗證碼失敗"}
	}

	subject := "帳戶綁定確認"
	bodyStr := fmt.Sprintf("%s/reset-password/%s", utils.Cfg.IrisDSURL, newPasswordVerify.PasswordVerifyCode)
	emailResponse, err := utils.TriggerEmail(fmt.Sprintf("%s/send-mail", utils.Cfg.IrisDSURL), user.Email, subject, bodyStr)
	if err != nil {
		fmt.Println("發送 Email 失敗:", err)
		return map[string]interface{}{"error": "發送郵件失敗"}
	}

	if errStr, ok := emailResponse["error"].(string); ok && errStr != "" {
		return map[string]interface{}{"error": "發送郵件失敗"}
	}
	return map[string]interface{}{"message": "驗證信已發送，請重設您的密碼"}
}

func SendEmailVerification(username string, db *gorm.DB) map[string]interface{} {
	var user models.User
	result := db.Where("username = ?", username).First(&user)
	if result.Error != nil {
		if errors.Is(result.Error, gorm.ErrRecordNotFound) {
			return map[string]interface{}{"error": "使用者不存在"}
		}
		return map[string]interface{}{"error": fmt.Sprintf("查詢時發生錯誤: %v", result.Error)}
	}

	if user.Email == "" {
		return map[string]interface{}{"error": "用戶未綁定 Email，請聯繫客服"}
	}

	var emailVerify models.EmailVerify
	db.Where("user_id = ?", user.ID).Order("valid_until desc").First(&emailVerify)

	currentTime := time.Now()
	if emailVerify.EmailVerifyCode != "" && currentTime.Before(emailVerify.ValidUntil) {
		return map[string]interface{}{"message": "驗證碼已發送，請檢查您的電子郵件"}
	}
	newEmailVerify := models.EmailVerify{
		EmailVerifyCode: utils.GenerateResetToken(6),
		ValidUntil:      currentTime.Add(15 * time.Minute),
		UserID:          user.ID,
	}
	if err := db.Create(&newEmailVerify).Error; err != nil {
		fmt.Println("新增驗證碼失敗:", err)
		return map[string]interface{}{"error": "新增驗證碼失敗"}
	}

	subject := "帳戶綁定確認"
	bodyStr := newEmailVerify.EmailVerifyCode
	emailResponse, err := utils.TriggerEmail(fmt.Sprintf("%s/send-mail", utils.Cfg.IrisDSURL), user.Email, subject, bodyStr)
	if err != nil {
		fmt.Println("發送 Email 失敗:", err)
		return map[string]interface{}{"error": "發送郵件失敗"}
	}

	if errVal, ok := emailResponse["error"]; ok && errVal != nil {
		return map[string]interface{}{"error": fmt.Sprintf("發送郵件失敗: %v", errVal)}
	}

	return map[string]interface{}{"message": "驗證碼已發送，請檢查電子郵件"}
}

func SendEmailCode(username string, db *gorm.DB, code string) gin.H {
	var user models.User
	if err := db.Where("username = ?", username).First(&user).Error; err != nil {
		return gin.H{"error": "使用者不存在"}
	}

	var emailVerify models.EmailVerify
	if err := db.Where("user_id = ?", user.ID).Order("valid_until desc").First(&emailVerify).Error; err != nil {
		return gin.H{"error": "未找到 Email 驗證紀錄"}
	}

	if code != emailVerify.EmailVerifyCode {
		return gin.H{"error": "驗證碼錯誤"}
	}

	if time.Now().After(emailVerify.ValidUntil) {
		return gin.H{"error": "驗證碼已過期"}
	}

	return gin.H{"message": "驗證成功，Email 已驗證"}
}

func SendRebindRequestEmail(username string, db *gorm.DB) (gin.H, int) {
	var user models.User
	if err := db.Where("username = ?", username).First(&user).Error; err != nil {
		return gin.H{"message": "找不到使用者"}, http.StatusNotFound
	}

	emailSubject := "【重新綁定 Email 請求】"
	emailBody := fmt.Sprintf(`
有使用者申請重新綁定 Email。

使用者帳號：%s
原本 Email：%s

請客服人員儘速手動處理此請求。
`, user.Username, user.Email)

	_, err := utils.TriggerEmail(fmt.Sprintf("%s/send-mail", utils.Cfg.IrisDSURL), "irisyen115@gmail.com", emailSubject, emailBody)
	if err != nil {
		return gin.H{"error": "發送電子郵件失敗"}, http.StatusInternalServerError
	}

	return gin.H{"message": "申請已送出，客服將會協助您重新綁定 Email"}, http.StatusOK
}
