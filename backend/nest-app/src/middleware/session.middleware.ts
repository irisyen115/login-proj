import { Injectable, NestMiddleware, Logger } from '@nestjs/common';
import { Request, Response, NextFunction } from 'express';
import { RedisService } from '../services/redis.service';
import { ConfigService } from '@nestjs/config';

@Injectable()
export class SessionMiddleware implements NestMiddleware {

  constructor(
    private readonly redisService: RedisService,
    private readonly configService: ConfigService,
  ) {}
  private readonly logger = new Logger(SessionMiddleware.name);

  async use(req: Request, res: Response, next: NextFunction) {
    const openPaths = [
      '/auth/google/callback',
      '/login',
      '/register',
      '/webhook',
      '/bind-email',
      '/verify-email',
      '/verify-code',
      '/request-bind-email',
      '/send-authentication',
      '/verify-google-email',
      '/request-bind-google-email',
      '/bind-google-email',
      '/reset-password',
    ];

    if (openPaths.some(path => req.originalUrl.startsWith(path))) {
      return next();
    }

    const sessionId = req.session?.session_id;

    if (sessionId) {
      const userId = await this.redisService.get(sessionId);
      if (userId) {
        (req as any).userId = parseInt(userId);
        await this.redisService.expire(sessionId, 1800);
        return next();
      } else {
        await this.redisService.del(sessionId);
        return res.redirect('/login');
      }
    } else {
      (req as any).userId = null;
      return res.redirect('/login');
    }
  }
}
