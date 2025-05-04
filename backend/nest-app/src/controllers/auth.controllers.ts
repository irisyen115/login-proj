import {
    Controller,
    Post,
    Body,
    Res,
    BadRequestException,
    Get,
  } from '@nestjs/common';
  import { AuthService } from '../services/auth.service';
  import { UserService } from '../services/user.service';
  import { Response } from 'express';

  @Controller()
  export class AuthController {
    constructor(
      private readonly authService: AuthService,
      private readonly userService: UserService
    ) {}

    @Post('auth/google/callback')
    async googleCallback(@Body('id_token') idToken: string, @Res() res: Response) {
      if (!idToken) throw new BadRequestException('缺少 id_token');

      const user = await this.authService.authenticateGoogleUser(idToken);
      if (!user) throw new BadRequestException('無效的 id_token');

      res
        .cookie('user_id', user.id, {
          httpOnly: true,
          secure: true,
          sameSite: 'none',
          maxAge: 3600 * 1000,
        })
        .cookie('role', user.role, {
          httpOnly: true,
          secure: true,
          sameSite: 'none',
          maxAge: 3600 * 1000,
        })
        .json({
          message: 'Google 登入成功',
          username: user.username,
          role: user.role,
          last_login: user.lastLogin?.toISOString() || null,
          login_count: user.loginCount,
        });
    }

    @Post('register')
    async register(@Body() data: any, @Res() res: Response) {
        const result = await this.userService.registerUser(data);
        const user = result.user;
        if (!user) throw new BadRequestException('註冊失敗');

        res
        .cookie('user_id', user.id, { httpOnly: true, secure: true, sameSite: 'strict' })
        .cookie('role', 'user', { httpOnly: true, secure: true, sameSite: 'strict' })
        .status(201)
        .json({ message: '註冊成功', user: user.username, role: 'user' });
    }

    @Post('login')
    async login(@Body() data: any, @Res() res: Response) {
        const result = await this.userService.loginUser(data);
        if (result.error) throw new BadRequestException(result.error);

        res
        .cookie('user_id', result.user_id, { httpOnly: true, secure: true, sameSite: 'strict' })
        .cookie('role', result.role, { httpOnly: true, secure: true, sameSite: 'strict' })
        .json({
            message: '登入成功',
            role: result.role,
            last_login: result.last_login,
            login_count: result.login_count,
        });
    }

    @Get('logout')
    logout(@Res() res: Response) {
        res
        .clearCookie('user_id')
        .clearCookie('role')
        .json({ message: '登出成功' });
    }
}