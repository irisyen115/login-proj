package models

import (
	"time"
)

type LineBindingUser struct {
	LineID    string    `gorm:"primaryKey;size:120;unique"`
	CreatedAt time.Time `gorm:"autoCreateTime"`
	UserID    uint      `gorm:"not null"`
	User      User      `gorm:"foreignKey:UserID"`
}
