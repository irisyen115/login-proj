package main

import (
	"fmt"
	"log"
	"net/http"
	"os"

	"golang-app/config"
	"golang-app/controllers"
	"golang-app/models"

	"github.com/gorilla/mux"
	"github.com/joho/godotenv"
	"github.com/rs/cors"
)

func init() {
	err := godotenv.Load()
	if err != nil {
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

	if _, err := os.Stat(cfg.UploadFolder); os.IsNotExist(err) {
		err := os.Mkdir(cfg.UploadFolder, os.ModePerm)
		if err != nil {
			log.Fatal("Failed to create upload folder: ", err)
		}
	}

	http.Handle("/", corsHandler)
	http.HandleFunc("/test", func(w http.ResponseWriter, r *http.Request) {
		log.Println("🧪 /test endpoint 被呼叫")
		fmt.Fprintln(w, "Golang API is working!")
	})

	log.Fatal(http.ListenAndServe("0.0.0.0:8082", nil))

}
