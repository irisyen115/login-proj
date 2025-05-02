package models

import (
	"time"
)

type EmailVerify struct {
	ID              uint      `gorm:"primaryKey"`
	CreatedAt       time.Time `gorm:"autoCreateTime"`
	ValidUntil      time.Time `gorm:"not null"`
	EmailVerifyCode string    `gorm:"size:50;not null"`
	UserID          uint      `gorm:"not null;index"`
	User            User      `gorm:"foreignKey:UserID"`
}

func (EmailVerify) TableName() string {
	return "email_verification"
}
