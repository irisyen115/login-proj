import {
    Controller,
    Post,
    Body,
    Res,
    BadRequestException,
    Get,
    Req,
    Logger,
  } from '@nestjs/common';
  import { AuthService } from '../services/auth.service';
  import { UserService } from '../services/user.service';
  import { RedisService } from '../services/redis.service';
  import { Response } from 'express';
  import { Request } from 'express';


  @Controller()
  export class AuthController {
    private readonly logger = new Logger(AuthController.name);
    constructor(
      private readonly authService: AuthService,
      private readonly userService: UserService,
      private readonly redisService: RedisService,
    ) {}

    @Post('auth/google/callback')
      async googleCallback(@Body('id_token') idToken: string,@Req() req: Request ,@Res() res: Response) {
      try {
        if (!idToken) throw new BadRequestException('缺少 id_token');

        const user = await this.authService.authenticateGoogleUser(idToken);
        if (!user) throw new BadRequestException('無效的 id_token');

        const sessionId = this.userService.generateSignedSessionId(user.id);
        req.session.session_id = sessionId;

        await this.redisService.set(sessionId, user.id.toString(), 1800);

        res
          .cookie('session_id', sessionId, {
            httpOnly: true,
            secure: true,
            sameSite: 'strict',
            maxAge: 1800 * 1000,
        })
          .json({
            message: 'Google 登入成功',
            username: user.username,
            role: user.role,
            last_login: user.lastLogin?.toISOString() || null,
            login_count: user.loginCount,
          });
    } catch (error) {
        console.error("Google 登入處理過程中發生錯誤:", error);
        res.status(500).json({ error: "伺服器錯誤，請稍後再試" });
      }
    }

    @Post('register')
    async register(@Body() data: any, @Res() res: Response) {
      try{
        const result = await this.userService.registerUser(data);
        const user = result.user;
        if (!user) throw new BadRequestException('註冊失敗');

        const sessionId = this.userService.generateSignedSessionId(user.id);
        await this.redisService.set(sessionId, user.id.toString(), 1800);

        res
        .cookie('session_id', sessionId, { httpOnly: true })
        .json({ message: '註冊成功', user: user.username, role: 'user' });
      } catch (error) {
        console.error("註冊處理過程中發生錯誤:", error);
        res.status(500).json({ error: "伺服器錯誤，請稍後再試" });
      }
    }

    @Post('login')
    async login(@Body() data: any, @Req() req: Request ,@Res() res: Response) {
      try {
        const result = await this.userService.loginUser(data);
        if (result.error) throw new BadRequestException(result.error);

        const user = result.user;
        if (!user) throw new BadRequestException('登入失敗');

        const sessionId = this.userService.generateSignedSessionId(user.id);
        req.session.session_id = sessionId;
        await this.redisService.set(sessionId, user.id.toString(), 1800);

        res
          .cookie('session_id', sessionId, { httpOnly: true })
          .json({
            message: '登入成功',
            role: result.role,
            last_login: user.lastLogin,
            login_count: user.loginCount,
          });
      } catch (error) {
        console.error("登入處理過程中發生錯誤:", error);
        res.status(500).json({ error: "伺服器錯誤，請稍後再試" });
      }

    }

    @Get('logout')
    logout(@Res() res: Response) {
      res.clearCookie('user_id', { httpOnly: true, secure: true, sameSite: 'strict' });
      res.clearCookie('role', { httpOnly: true, secure: true, sameSite: 'strict' });
      return res.json({ message: '登出成功' });
    }
}