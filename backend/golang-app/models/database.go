package models

import (
	"fmt"
	"log"
	"os"

	"gorm.io/driver/postgres"
	"gorm.io/gorm"
)

var DB *gorm.DB

func InitDB() {
	dsn := os.Getenv("SQLALCHEMY_DATABASE_URI")
	db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{})
	if err != nil {
		log.Fatalf("無法連接資料庫: %v", err)
	}

	DB = db
	fmt.Println("✅ 成功連接到資料庫")

	err = db.AutoMigrate(
		&User{},
		&EmailVerify{},
		&PasswordVerify{},
		&LineBindingUser{},
	)
	if err != nil {
		log.Fatalf("資料表建立失敗: %v", err)
	}

	fmt.Println("📦 資料表建立完成")
}
