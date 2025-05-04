import {
    Controller,
    Get,
    Req,
    Res,
    UseGuards,
    UnauthorizedException,
  } from '@nestjs/common';
  import { UserService } from '../services/user.service';
  import { Response, Request } from 'express';

  @Controller('user')
  export class UserController {
    constructor(private readonly userService: UserService) {}

    @Get('users')
    async getUsers(@Req() req: Request, @Res() res: Response) {
      const userId = req['user_id'];
      if (!userId) {
        throw new UnauthorizedException('未授權');
      }

      const result = await this.userService.fetchUsersData(userId);

      if ('error' in result) {
        return res.status(404).json(result);
      }

      return res.json(result);
    }
  }
