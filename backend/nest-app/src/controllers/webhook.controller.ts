import {
  Body,
  Controller,
  Post,
  Res,
  HttpStatus,
  Req,
} from '@nestjs/common';
import { Response } from 'express';
import { WebhookService } from '../services/webhook.service';
import { AuthService } from '../services/auth.service';
import { UserService } from '../services/user.service';
import { RedisService } from '../services/redis.service';
import { Request } from 'express';

@Controller()
  export class WebhookController {
    constructor(
      private readonly webhookService: WebhookService,
      private readonly authService: AuthService,
      private readonly userService: UserService,
      private readonly redisService: RedisService,
    ) {}

  @Post('webhook')
  async webhook(@Body() body: any, @Res() res: Response) {
    const timeout = new Promise((_, reject) =>
      setTimeout(() => reject(new Error('Request timeout')), 5000),
    );

    try {
      const result = await Promise.race([
        this.webhookService.handleWebhookEvent(body),
        timeout,
      ]);
      return res.json(result);
    } catch (error) {
      console.error('Webhook處理錯誤:', error);
      return res
        .status(HttpStatus.INTERNAL_SERVER_ERROR)
        .json({ error: `Webhook 處理發生錯誤: ${error.message || error.toString()}` });
    }
  }

  @Post('bind-google-email')
  async bindGoogleEmail(@Body() body: any, @Req() req: Request, @Res() res: Response) {
    if (!body) {
      return res.status(400).json({ error: 'no data' });
    }

    for (const key of ['google_token', 'uid']) {
      if (!body[key]) {
        return res.status(400).json({ error: `缺少必要的資料(${key})` });
      }
    }

    try {
      const user = await this.authService.identifyGoogleUserByToken(body);
      if (!user) {
        return res.status(400).json({ error: 'Google 用戶認證失敗' });
      }

      const bindResult = await this.authService.bindLineUidToUser(body.uid, user);
      const sessionId = this.userService.generateSignedSessionId(user.id);
      req.session.session_id = sessionId;
      await this.redisService.set(sessionId, user.id.toString(), 1800);

      return res
        .status(HttpStatus.OK)
        .cookie('session_id', sessionId, { httpOnly: true })
        .json(bindResult);
    } catch (e) {
      return res
        .status(500)
        .json({ error: `伺服器錯誤: ${e.message || e.toString()}` });
    }
  }

  @Post('bind-email')
  async bindEmail(@Body() body: any, @Req() req: Request, @Res() res: Response) {
    if (!body) {
      return res.status(400).json({ error: 'no data' });
    }

    for (const key of ['username', 'password', 'uid']) {
      if (!body[key]) {
        return res.status(400).json({ error: `缺少必要的資料(${key})` });
      }
    }

    try {
      const user = await this.authService.identifyGoogleUserByToken(body);
      if (!user) {
        return res.status(400).json({ error: 'Google 用戶認證失敗' });
      }

      const bindResult = await this.authService.bindLineUidToUser(body.uid, user);
      const sessionId = this.userService.generateSignedSessionId(user.id);
      req.session.session_id = sessionId;
      await this.redisService.set(sessionId, user.id.toString(), 1800);

      return res
        .status(HttpStatus.OK)
        .cookie('session_id', sessionId, { httpOnly: true })
        .json(bindResult);

    } catch (e) {
      return res
        .status(500)
        .json({ error: `伺服器錯誤: ${e.message || e.toString()}` });
    }
  }
}