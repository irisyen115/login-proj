package models

import (
	"encoding/json"
	"time"

	"golang.org/x/crypto/bcrypt"
)

type Role string

const (
	RoleUser  Role = "user"
	RoleAdmin Role = "admin"
	RoleGuest Role = "guest"
)

type User struct {
	ID           uint       `gorm:"primaryKey" json:"id"`
	Username     string     `gorm:"size:50;not null" json:"username"`
	PasswordHash string     `gorm:"type:text" json:"password_hash"`
	Role         Role       `gorm:"type:role_enum;default:user" json:"role"`
	CreatedAt    time.Time  `gorm:"autoCreateTime" json:"created_at"`
	UpdatedAt    time.Time  `gorm:"autoUpdateTime" json:"updated_at"`
	LastLogin    *time.Time `json:"last_login"`
	LoginCount   int        `gorm:"default:0" json:"login_count"`
	ProfileImage *string    `gorm:"size:255" json:"profile_image"`
	PictureName  *string    `gorm:"size:255" json:"picture_name"`
	Email        *string    `gorm:"size:254" json:"email"`

	PasswordVerifications []PasswordVerify  `gorm:"constraint:OnDelete:CASCADE;" json:"-"`
	EmailVerifications    []EmailVerify     `gorm:"constraint:OnDelete:CASCADE;" json:"-"`
	LineBindingUsers      []LineBindingUser `gorm:"constraint:OnDelete:CASCADE;" json:"-"`
}

func (u *User) SetPassword(password string) error {
	hash, err := bcrypt.GenerateFromPassword([]byte(password), bcrypt.DefaultCost)
	if err != nil {
		return err
	}
	u.PasswordHash = string(hash)
	return nil
}

func (u *User) CheckPassword(password string) bool {
	err := bcrypt.CompareHashAndPassword([]byte(u.PasswordHash), []byte(password))
	return err == nil
}

func (u *User) UpdateLastLogin() {
	now := time.Now()
	u.LastLogin = &now
	u.LoginCount++
}

func (u *User) ToJSON() (string, error) {
	data, err := json.Marshal(u)
	return string(data), err
}

func UserFromJSON(jsonStr string) (*User, error) {
	var user User
	err := json.Unmarshal([]byte(jsonStr), &user)
	return &user, err
}
