package models

import (
	"time"
)

type LineBindingUser struct {
	ID        uint      `gorm:"primaryKey"`
	LineID    string    `gorm:"size:120;unique"`
	CreatedAt time.Time `gorm:"autoCreateTime"`
	UserID    uint      `gorm:"not null"`
	User      User      `gorm:"foreignKey:UserID"`
}

func (LineBindingUser) TableName() string {
	return "line_binding_user"
}
