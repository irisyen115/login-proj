package services

import (
	"fmt"
	"golang-app/models"
	"golang-app/utils"
	"io"
	"mime/multipart"
	"os"
	"path/filepath"

	_ "github.com/jinzhu/gorm/dialects/sqlite"
	"gorm.io/gorm"
)

func SaveUserAvatar(db *gorm.DB, userID uint, file *multipart.FileHeader) (string, error) {
	filename := fmt.Sprintf("%d.jpg", userID)
	filepath := filepath.Join(utils.Cfg.UploadFolder, filename)

	if err := saveUploadedFile(file, filepath); err != nil {
		return "", err
	}

	var user models.User
	if err := db.First(&user, userID).Error; err != nil {
		return "", err
	}

	user.ProfileImage = &filepath
	user.PictureName = &filename

	if err := db.Save(&user).Error; err != nil {
		return "", err
	}

	return filepath, nil
}

func saveUploadedFile(file *multipart.FileHeader, dst string) error {
	src, err := file.Open()
	if err != nil {
		return err
	}
	defer src.Close()

	out, err := os.Create(dst)
	if err != nil {
		return err
	}
	defer out.Close()

	_, err = io.Copy(out, src)
	return err
}

func GetUserImageService(user *models.User) string {
	if user.ProfileImage != nil && *user.ProfileImage != "" {
		imagePath := filepath.Join(utils.Cfg.UploadFolder, *user.PictureName)
		if _, err := os.Stat(imagePath); err == nil {
			return *user.PictureName
		}
	}
	return ""
}
