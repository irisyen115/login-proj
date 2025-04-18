package config

import (
	"fmt"
	"log"
	"os"
	"strconv"
)

type Config struct {
	SecretKey                    string
	SQLAlchemyDatabaseURI        string
	SQLAlchemyTrackModifications bool
	GoogleClientID               string
	GoogleClientSecret           string
	GoogleRedirectURI            string
	LineReplyURL                 string
	LineAccessToken              string
	IrisDSURL                    string
	RedisHost                    string
	RedisPort                    int
	UploadFolder                 string
}

var GlobalConfig *Config

func LoadConfig() *Config {
	config := &Config{
		SecretKey:                    getEnv("SECRET_KEY", "default_secret"),
		SQLAlchemyDatabaseURI:        getEnv("SQLALCHEMY_DATABASE_URI", ""),
		SQLAlchemyTrackModifications: false,
		GoogleClientID:               getEnv("GOOGLE_CLIENT_ID", ""),
		GoogleClientSecret:           getEnv("GOOGLE_CLIENT_SECRET", ""),
		GoogleRedirectURI:            getEnv("GOOGLE_REDIRECT_URI", ""),
		LineReplyURL:                 getEnv("LINE_REPLY_URL", ""),
		LineAccessToken:              getEnv("LINE_ACCESS_TOKEN", ""),
		IrisDSURL:                    getEnv("IRIS_DS_SERVER_URL", ""),
		RedisHost:                    getEnv("REDIS_HOST", "localhost"),
		RedisPort:                    getEnvAsInt("REDIS_PORT", 6379),
		UploadFolder:                 fmt.Sprintf("%s/uploads", getWorkingDirectory()),
	}
	GlobalConfig = config

	return config
}

func getEnv(key string, defaultValue string) string {
	value := os.Getenv(key)
	if value == "" {
		return defaultValue
	}
	return value
}

func getEnvAsInt(key string, defaultValue int) int {
	value := os.Getenv(key)
	if value == "" {
		return defaultValue
	}
	intValue, err := strconv.Atoi(value)
	if err != nil {
		log.Printf("Error converting %s to int, using default value: %d", key, defaultValue)
		return defaultValue
	}
	return intValue
}

func getWorkingDirectory() string {
	wd, err := os.Getwd()
	if err != nil {
		log.Fatal("Error getting working directory:", err)
	}
	return wd
}
