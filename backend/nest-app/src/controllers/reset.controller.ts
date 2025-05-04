import {
    Controller,
    Post,
    Param,
    Body,
    BadRequestException,
  } from '@nestjs/common';
  import { ResetService } from '../services/reset.service';

  @Controller('reset-password')
  export class ResetController {
    constructor(private readonly resetService: ResetService) {}

    @Post(':passwordVerifyCode')
    async resetPassword(
      @Param('passwordVerifyCode') code: string,
      @Body('password') newPassword: string,
    ) {
      if (!newPassword) {
        throw new BadRequestException('請提供新密碼');
      }

      const result = await this.resetService.resetUserPassword(code, newPassword);
      if (result.error) {
        throw new BadRequestException(result.error);
      }

      return { message: result.message };
    }
  }
