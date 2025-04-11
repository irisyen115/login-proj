package models

import (
	"time"
)

type PasswordVerify struct {
	ID                 uint      `gorm:"primaryKey"`
	CreatedAt          time.Time `gorm:"autoCreateTime"`
	ValidUntil         time.Time `gorm:"not null"`
	PasswordVerifyCode string    `gorm:"size:50"`
	UserID             uint      `gorm:"not null;unique"`
	User               User      `gorm:"foreignKey:UserID"`
}
