package models

import (
	"golang-app/config"
	"golang-app/utils"
	"log"

	"gorm.io/driver/postgres"
	"gorm.io/gorm"
)

var db *gorm.DB

func InitDB() {
	cfg := config.LoadConfig()
	dsn := cfg.SQLAlchemyDatabaseURI // 確保這個是正確的資料庫連接字符串

	var err error
	db, err = gorm.Open(postgres.Open(dsn), &gorm.Config{})
	if err != nil {
		log.Fatalf("資料庫連接失敗: %v", err)
	}
	utils.Db = db

	// 確保資料庫成功連接
	if db == nil {
		log.Fatal("資料庫未成功初始化")
	}
}
