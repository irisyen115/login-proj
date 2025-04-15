package models

import (
	"time"
)

type PasswordVerify struct {
	ID                 uint      `gorm:"primaryKey"`
	CreatedAt          time.Time `gorm:"autoCreateTime"`
	ValidUntil         time.Time `gorm:"not null"`
	PasswordVerifyCode string    `gorm:"size:50;not null"`
	UserID             uint      `gorm:"not null;index"`
	User               User      `gorm:"foreignKey:UserID"`
}

func (PasswordVerify) TableName() string {
	return "password_verification"
}
