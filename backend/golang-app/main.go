package main

import (
	"context"
	"log"
	"net/http"
	"os"
	"runtime/debug"
	"strings"
	"time"

	"golang-app/config"
	"golang-app/controllers"
	"golang-app/models"
	"golang-app/utils"

	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
	"github.com/go-redis/redis/v8"
	"github.com/joho/godotenv"
)

var ctx = context.Background()

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

func SessionMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		openPaths := []string{
			"/auth/google/callback",
			"/login",
			"/register",
			"/webhook",
			"/bind-email",
			"/bind-google-email",
		}

		for _, path := range openPaths {
			if strings.HasPrefix(c.Request.URL.Path, path) {
				c.Next()
				return
			}
		}

		sessionID, err := c.Cookie("session_id")
		log.Printf("Session ID: %s", sessionID)

		if err != nil || sessionID == "" {
			log.Println("Session ID is None, user is not authenticated.")
			c.Redirect(http.StatusFound, "/login")
			c.Abort()
			return
		}

		userID, err := utils.RedisClient.Get(ctx, sessionID).Result()
		log.Printf("User ID from Redis: %s", userID)

		if err == redis.Nil || userID == "" {
			log.Println("Invalid session ID, clearing session.")
			clearSession(c, sessionID)
			c.Redirect(http.StatusFound, "/login")
			c.Abort()
			return
		} else if err != nil {
			log.Println("Redis error:", err)
			c.AbortWithStatus(http.StatusInternalServerError)
			return
		}

		utils.RedisClient.Expire(ctx, sessionID, 30*time.Minute)

		c.Set("user_id", userID)
		c.Next()
	}
}

func clearSession(c *gin.Context, sessionID string) {
	c.Set("user_id", nil)
	utils.RedisClient.Del(ctx, sessionID)
	c.SetCookie("session_id", "", -1, "/", "", false, true)
	log.Println("Session ID cleared and user logged out.")
}

func main() {
	cfg := config.LoadConfig()
	utils.InitRedis(cfg)
	utils.Cfg = cfg
	r := gin.New()
	r.GET("/login", func(c *gin.Context) {
		c.String(http.StatusOK, "Login Page")
	})

	r.Use(gin.Logger())
	r.Use(gin.CustomRecoveryWithWriter(os.Stderr, func(c *gin.Context, err interface{}) {
		log.Printf("🔥 panic recovered: %v\n", err)
		debug.PrintStack()
		c.AbortWithStatusJSON(500, gin.H{"error": "Internal Server Error"})
	}))
	r.Use(SessionMiddleware())

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

	if err := r.Run("0.0.0.0:5000"); err != nil {
		log.Fatalf("Internal Server Error: %v", err)
	}
}
