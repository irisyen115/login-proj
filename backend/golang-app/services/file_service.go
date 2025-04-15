package services

import (
	"fmt"
	"golang-app/models"
	"golang-app/utils"
	"io"
	"log"
	"mime/multipart"
	"os"
	"path"

	_ "github.com/jinzhu/gorm/dialects/sqlite"
	"gorm.io/gorm"
)

func SaveUserAvatar(db *gorm.DB, userID uint, file *multipart.FileHeader) (string, error) {
	uploadFolder := utils.Cfg.UploadFolder

	filename := fmt.Sprintf("%d.jpg", userID)
	filepath := path.Join(uploadFolder, filename)

	if err := saveUploadedFile(file, filepath); err != nil {
		return "", err
	}

	var user models.User
	if err := db.First(&user, userID).Error; err != nil {
		return "", err
	}

	user.ProfileImage = filepath
	user.PictureName = filename

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
	log.Println(">> 呼叫到 GetUserImageService 囉！")

	if user == nil {
		log.Println("User is nil")
		return ""
	}

	log.Printf("User ProfileImage value: %v", user.ProfileImage)
	if user.ProfileImage != "" {
		imagePath := user.ProfileImage
		log.Printf("Profile image path: %s", imagePath)

		if _, err := os.Stat(imagePath); err == nil {
			log.Println("Image exists")
			return user.PictureName
		} else {
			log.Printf("Image does not exist: %s, err: %v", imagePath, err)
		}
	} else {
		log.Println("ProfileImage is nil or empty")
	}

	return ""
}
