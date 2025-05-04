import {
    Body,
    Controller,
    Post,
    Res,
    HttpStatus,
  } from '@nestjs/common';
  import { Response } from 'express';
  import { WebhookService } from '../services/webhook.service';
  import { AuthService } from '../services/auth.service';

  @Controller('webhook')
  export class WebhookController {
    constructor(
      private readonly webhookService: WebhookService,
      private readonly authService: AuthService,
    ) {}

    @Post()
    async webhook(@Body() body: any, @Res() res: Response) {
      const result = await this.webhookService.handleWebhookEvent(body);
      return result;
    }

    @Post('bind-google-email')
    async bindGoogleEmail(@Body() body: any, @Res() res: Response) {
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
        const bindResult = await this.authService.bindLineUidToUser(body.uid, user);
        return res.json(bindResult);
      } catch (e) {
        return res
          .status(500)
          .json({ error: `伺服器錯誤: ${e.message || e.toString()}` });
      }
    }

    @Post('bind-email')
    async bindEmail(@Body() body: any, @Res() res: Response) {
      if (!body) {
        return res.status(400).json({ error: 'no data' });
      }

      for (const key of ['username', 'password', 'uid']) {
        if (!body[key]) {
          return res.status(400).json({ error: `缺少必要的資料(${key})` });
        }
      }

      try {
        const user = await this.authService.identifyGoogleUserByToken(body); // 注意：此邏輯是否應改為帳密驗證？
        const bindResult = await this.authService.bindLineUidToUser(body.uid, user);
        return res.json(bindResult);
      } catch (e) {
        return res
          .status(500)
          .json({ error: `伺服器錯誤: ${e.message || e.toString()}` });
      }
    }
  }
