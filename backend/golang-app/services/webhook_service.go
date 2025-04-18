package services

import (
	"bytes"
	"encoding/json"
	"fmt"
	"golang-app/utils"
	"net/http"

	"github.com/gin-gonic/gin"
)

type LineEvent struct {
	Events []struct {
		Type    string `json:"type"`
		Message struct {
			Text string `json:"text"`
		} `json:"message"`
		Source struct {
			UserID string `json:"userId"`
		} `json:"source"`
		ReplyToken string `json:"replyToken"`
	} `json:"events"`
}

func replyMessage(replyToken, text string) error {
	payload := map[string]interface{}{
		"replyToken": replyToken,
		"messages": []map[string]string{
			{
				"type": "text",
				"text": text,
			},
		},
	}

	jsonPayload, _ := json.Marshal(payload)
	req, err := http.NewRequest("POST", utils.Cfg.LineReplyURL, bytes.NewBuffer(jsonPayload))
	if err != nil {
		return err
	}

	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Authorization", fmt.Sprintf("Bearer %s", utils.Cfg.LineAccessToken))

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	return nil
}

func HandleWebhookEvent(c *gin.Context) {
	var body LineEvent

	if err := c.ShouldBindJSON(&body); err != nil {
		c.String(http.StatusInternalServerError, "Internal Server Error")
		return
	}

	for _, event := range body.Events {
		if event.Type == "message" {
			text := event.Message.Text
			uid := event.Source.UserID
			if contains(text, "綁定") {
				loginURL := fmt.Sprintf("%s/Line-login?uid=%s", utils.Cfg.IrisDSURL, uid)
				replyText := fmt.Sprintf("請點擊以下網址進行綁定：\n%s", loginURL)
				replyMessage(event.ReplyToken, replyText)
			}
		}
	}

	c.String(http.StatusOK, "OK")
}

func contains(source, substr string) bool {
	return bytes.Contains([]byte(source), []byte(substr))
}
