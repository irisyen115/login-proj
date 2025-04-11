package services

import (
	"bytes"
	"encoding/json"
	"fmt"
	"golang-app/utils"
	"log"
	"net/http"
	"strings"
	"time"
)

type LineEvent struct {
	ReplyToken string `json:"replyToken"`
	Source     struct {
		UserID string `json:"userId"`
	} `json:"source"`
	Message struct {
		Text string `json:"text"`
	} `json:"message"`
}

type LineWebhookRequest struct {
	Events []LineEvent `json:"events"`
}

func replyMessage(replyToken string, text string) error {
	payload := map[string]interface{}{
		"replyToken": replyToken,
		"messages": []map[string]interface{}{
			{
				"type": "text",
				"text": text,
			},
		},
	}

	payloadBytes, err := json.Marshal(payload)
	if err != nil {
		return fmt.Errorf("failed to marshal payload: %v", err)
	}

	req, err := http.NewRequest("POST", utils.Cfg.LineReplyURL, bytes.NewBuffer(payloadBytes))
	if err != nil {
		return fmt.Errorf("failed to create request: %v", err)
	}
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Authorization", "Bearer "+utils.Cfg.LineAccessToken)

	client := &http.Client{Timeout: 10 * time.Second}
	resp, err := client.Do(req)
	if err != nil {
		return fmt.Errorf("failed to send reply: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("received non-OK status: %v", resp.StatusCode)
	}

	return nil
}

func HandleWebhookEvent(body []byte) (string, int) {
	var webhookRequest LineWebhookRequest
	if err := json.Unmarshal(body, &webhookRequest); err != nil {
		log.Printf("Error parsing request body: %v", err)
		return "Internal Server Error", http.StatusInternalServerError
	}

	for _, event := range webhookRequest.Events {
		if event.Message.Text != "" && strings.Contains(event.Message.Text, "綁定") {
			loginURL := fmt.Sprintf("%s/Line-login?uid=%s", utils.Cfg.IrisDSURL, event.Source.UserID)
			replyText := fmt.Sprintf("請點擊以下網址進行綁定：\n%s", loginURL)
			if err := replyMessage(event.ReplyToken, replyText); err != nil {
				log.Printf("Failed to reply message: %v", err)
				return "Internal Server Error", http.StatusInternalServerError
			}
		}
	}

	return "OK", http.StatusOK
}
