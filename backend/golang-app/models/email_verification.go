package models

import (
	"time"
)

type EmailVerify struct {
	ID              uint      `gorm:"primaryKey"`
	CreatedAt       time.Time `gorm:"autoCreateTime"`
	ValidUntil      time.Time `gorm:"not null"`
	EmailVerifyCode string    `gorm:"size:50"`
	UserID          uint      `gorm:"unique;not null"`
	User            User      `gorm:"foreignKey:UserID"`
}
