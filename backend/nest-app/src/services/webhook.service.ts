import { Injectable } from '@nestjs/common';
import axios from 'axios';
import { ConfigService } from '@nestjs/config';

@Injectable()
export class WebhookService {
  private readonly lineReplyUrl: string;
  private readonly lineAccessToken: string;
  private readonly irisServerUrl: string;

  constructor(private readonly configService: ConfigService) {
    this.lineReplyUrl = this.configService.get<string>('LINE_REPLY_URL') ?? '';
    this.lineAccessToken = this.configService.get<string>('LINE_ACCESS_TOKEN') ?? '';
    this.irisServerUrl = this.configService.get<string>('IRIS_DS_SERVER_URL') ?? '';
  }

  async handleWebhookEvent(body: any) {
    const events = body.events || [];

    for (const event of events) {
      if (event.type === 'message') {
        const text = event.message.text;
        const uid = event.source.userId;

        if (text.includes('綁定')) {
          const loginUrl = `${this.irisServerUrl}/Line-login?uid=${uid}`;
          await this.replyMessage(event.replyToken, `請點擊以下網址進行綁定：\n${loginUrl}`);
        }
      }
    }
  }

  async replyMessage(replyToken: string, text: string) {
    const headers = {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${this.lineAccessToken}`,
    };

    const payload = {
      replyToken,
      messages: [{ type: 'text', text }],
    };

    await axios.post(this.lineReplyUrl, payload, { headers });
  }
}
