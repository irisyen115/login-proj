package main

import (
<<<<<<< HEAD
	"log"
	"os"
	"runtime/debug"
	"strconv"
=======
	"fmt"
	"log"
	"net/http"
	"os"
>>>>>>> a686d04e (create a golang backend #102)

	"golang-app/config"
	"golang-app/controllers"
	"golang-app/models"
<<<<<<< HEAD
	"golang-app/utils"

	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
	"github.com/joho/godotenv"
=======

	"github.com/gorilla/mux"
	"github.com/joho/godotenv"
	"github.com/rs/cors"
>>>>>>> a686d04e (create a golang backend #102)
)

func init() {
	err := godotenv.Load()
	if err != nil {
<<<<<<< HEAD
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
=======
		log.Fatal("Error loading .env file")
	}

	models.InitDB()
}

func main() {
	r := mux.NewRouter()

	corsHandler := cors.New(cors.Options{
		AllowedOrigins: []string{os.Getenv("IRIS_DS_SERVER_URL")},
		AllowedMethods: []string{"GET", "POST", "PUT", "DELETE", "OPTIONS"},
		AllowedHeaders: []string{"Content-Type", "Authorization"},
	}).Handler(r)

	r.HandleFunc("/auth", controllers.AuthHandlerHTTP).Methods("GET", "POST")
	r.HandleFunc("/webhook", controllers.WebhookHandler).Methods("POST")
	r.HandleFunc("/user", controllers.UserHandlerHTTP).Methods("GET", "POST")
	r.HandleFunc("/file", controllers.FileHandlerHTTP).Methods("GET", "POST")
	r.HandleFunc("/email", controllers.EmailHandlerHTTP).Methods("POST")
	r.HandleFunc("/reset", controllers.ResetHandlerHTTP).Methods("POST")

	cfg := config.LoadConfig()
>>>>>>> a686d04e (create a golang backend #102)

	if _, err := os.Stat(cfg.UploadFolder); os.IsNotExist(err) {
		err := os.Mkdir(cfg.UploadFolder, os.ModePerm)
		if err != nil {
			log.Fatal("Failed to create upload folder: ", err)
		}
	}

<<<<<<< HEAD
	r.GET("/test", func(c *gin.Context) {
		log.Println("🧪 /test endpoint 被呼叫")
		c.String(200, "Golang API is working!")
	})

	if err := r.Run("0.0.0.0:5000"); err != nil {
		log.Fatalf("Internal Server Error: %v", err)
	}
=======
	http.Handle("/", corsHandler)
	http.HandleFunc("/test", func(w http.ResponseWriter, r *http.Request) {
		log.Println("🧪 /test endpoint 被呼叫")
		fmt.Fprintln(w, "Golang API is working!")
	})

	log.Fatal(http.ListenAndServe("0.0.0.0:8082", nil))

>>>>>>> a686d04e (create a golang backend #102)
}
