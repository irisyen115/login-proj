package main

import (
	"log"
	"os"
	"runtime/debug"
	"strconv"

	"golang-app/config"
	"golang-app/controllers"
	"golang-app/models"
	"golang-app/utils"

	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
	"github.com/joho/godotenv"
)

func init() {
	err := godotenv.Load()
	if err != nil {
		log.Println("⚠️ .env file not loaded:", err)
	} else {
		log.Println("✅ .env file loaded successfully")
		log.Println("🔍 REDIS_HOST =", os.Getenv("REDIS_HOST"))
		log.Println("🔍 REDIS_PORT =", os.Getenv("REDIS_PORT"))
	}

	models.InitDB()
	log.Println("✅ models.InitDB() 執行完畢")
}

func UserIDMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		userIDStr, err := c.Cookie("user_id")
		if err != nil || userIDStr == "" {
			c.Next()
			return
		}

		userID, err := strconv.Atoi(userIDStr)
		if err == nil {
			c.Set("user_id", uint(userID))
		}

		c.Next()
	}
}

func main() {
	cfg := config.LoadConfig()
	utils.InitRedis(cfg)
	utils.Cfg = cfg
	r := gin.New()
	r.Use(gin.Logger())
	r.Use(gin.CustomRecoveryWithWriter(os.Stderr, func(c *gin.Context, err interface{}) {
		log.Printf("🔥 panic recovered: %v\n", err)
		debug.PrintStack()
		c.AbortWithStatusJSON(500, gin.H{"error": "Internal Server Error"})
	}))
	r.Use(UserIDMiddleware())

	r.Use(cors.New(cors.Config{
		AllowOrigins:     []string{os.Getenv("IRIS_DS_SERVER_URL")},
		AllowMethods:     []string{"GET", "POST", "PUT", "DELETE", "OPTIONS"},
		AllowHeaders:     []string{"Origin", "Content-Type", "Authorization"},
		AllowCredentials: true,
	}))

	controllers.RegisterAuthRoutes(r)
	controllers.RegisterEmailRoutes(r)
	controllers.RegisterFileRoutes(r)
	controllers.RegisterResetRoutes(r)
	controllers.RegisterUserRoutes(r)
	controllers.RegisterWebhookRoutes(r)

	if _, err := os.Stat(cfg.UploadFolder); os.IsNotExist(err) {
		err := os.Mkdir(cfg.UploadFolder, os.ModePerm)
		if err != nil {
			log.Fatal("Failed to create upload folder: ", err)
		}
	}

	r.GET("/test", func(c *gin.Context) {
		log.Println("🧪 /test endpoint 被呼叫")
		c.String(200, "Golang API is working!")
	})

	if err := r.Run("0.0.0.0:5000"); err != nil {
		log.Fatalf("Internal Server Error: %v", err)
	}
}
