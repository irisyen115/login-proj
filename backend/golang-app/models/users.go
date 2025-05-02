package models

import (
	"database/sql/driver"
	"encoding/json"
	"fmt"
	"strings"
	"time"

	"golang.org/x/crypto/bcrypt"
)

type Role string

const (
	RoleUser  Role = "user"
	RoleAdmin Role = "admin"
	RoleGuest Role = "guest"
)

func (r *Role) UnmarshalJSON(b []byte) error {
	s := strings.Trim(string(b), `"`)
	if s == "" {
		*r = ""
		return nil
	}
	switch Role(s) {
	case RoleUser, RoleAdmin, RoleGuest:
		*r = Role(s)
		return nil
	default:
		return fmt.Errorf("未知的角色: %s", s)
	}
}

func (r Role) MarshalJSON() ([]byte, error) {
	if r == "" {
		return []byte(`""`), nil
	}
	if r == RoleUser || r == RoleAdmin || r == RoleGuest {
		return json.Marshal(string(r))
	}
	return nil, fmt.Errorf("未知的角色: %s", r)
}

func (r Role) Value() (driver.Value, error) {
	return string(r), nil
}

func (r *Role) Scan(value interface{}) error {
	if value == nil {
		*r = RoleUser
		return nil
	}

	str, ok := value.(string)
	if !ok {
		bytes, ok := value.([]byte)
		if ok {
			str = string(bytes)
		} else {
			return fmt.Errorf("無法將 %v 轉為 Role", value)
		}
	}
	switch Role(str) {
	case RoleUser, RoleAdmin, RoleGuest:
		*r = Role(str)
		return nil
	default:
		return fmt.Errorf("未知的角色: %s", str)
	}
}

type User struct {
	ID           uint       `gorm:"primaryKey" json:"id"`
	Username     string     `gorm:"size:50;not null" json:"username"`
	PasswordHash string     `gorm:"type:text" json:"password_hash"`
	Role         Role       `gorm:"type:role_enum;default:user" json:"role"`
	CreatedAt    CustomTime `gorm:"autoCreateTime" json:"created_at"`
	UpdatedAt    CustomTime `gorm:"autoUpdateTime" json:"updated_at"`
	LastLogin    CustomTime `json:"last_login"`
	LoginCount   int        `gorm:"default:0" json:"login_count"`
	ProfileImage string     `gorm:"size:255" json:"profile_image"`
	PictureName  string     `gorm:"size:255" json:"picture_name"`
	Email        string     `gorm:"size:254" json:"email"`

	PasswordVerifications []PasswordVerify  `gorm:"constraint:OnDelete:CASCADE;" json:"-"`
	EmailVerifications    []EmailVerify     `gorm:"constraint:OnDelete:CASCADE;" json:"-"`
	LineBindingUsers      []LineBindingUser `gorm:"constraint:OnDelete:CASCADE;" json:"-"`
}

func NewUser(username string, email string, password string) (*User, error) {

	user := &User{
		Username: username,
		Email:    email,
	}

	if password != "" {
		if err := user.SetPassword(password); err != nil {
			return nil, err
		}
	}

	return user, nil
}

type CustomTime time.Time

func (ct *CustomTime) UnmarshalJSON(b []byte) error {
	s := strings.Trim(string(b), `"`)
	if s == "null" || s == "" {
		*ct = CustomTime(time.Time{})
		return nil
	}

	formats := []string{
		time.RFC3339Nano,
		"2006-01-02T15:04:05.999999",
		"2006-01-02T15:04:05",
		"2006-01-02 15:04:05",
	}

	for _, format := range formats {
		if t, err := time.Parse(format, s); err == nil {
			*ct = CustomTime(t)
			return nil
		}
	}

	return fmt.Errorf("無法解析時間格式: %s", s)
}

func (ct CustomTime) MarshalJSON() ([]byte, error) {
	t := time.Time(ct)
	return []byte(`"` + t.UTC().Format(time.RFC3339) + `"`), nil
}

func (ct CustomTime) IsZero() bool {
	return time.Time(ct).IsZero()
}

func (ct CustomTime) Value() (driver.Value, error) {
	t := time.Time(ct)
	if t.IsZero() {
		return nil, nil
	}
	return t, nil
}

func (ct *CustomTime) Scan(value interface{}) error {
	if value == nil {
		*ct = CustomTime(time.Time{})
		return nil
	}
	switch v := value.(type) {
	case time.Time:
		*ct = CustomTime(v)
		return nil
	default:
		return fmt.Errorf("cannot convert %v to CustomTime", value)
	}
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
	u.LastLogin = CustomTime(time.Now())
	u.LoginCount++
}

func (u *User) ToJSON() (string, error) {
	data, err := json.Marshal(u)
	return string(data), err
}

func UserFromJSON(jsonStr string) (*User, error) {
	var user User
	err := json.Unmarshal([]byte(jsonStr), &user)
	if err != nil {
		return nil, err
	}
	fmt.Printf("[DEBUG] 還原後的使用者 Role: %s\n", user.Role)
	return &user, nil
}
