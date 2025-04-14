package models

import (
	"golang-app/config"
	"log"

	"gorm.io/driver/postgres"
	"gorm.io/gorm"
)

var DB *gorm.DB

func InitDB() {
	cfg := config.LoadConfig()
	dsn := cfg.SQLAlchemyDatabaseURI

	var err error
	DB, err = gorm.Open(postgres.Open(dsn), &gorm.Config{})
	if err != nil {
		log.Fatalf("資料庫連接失敗: %v", err)
	}
	DB = DB.Debug()

}
