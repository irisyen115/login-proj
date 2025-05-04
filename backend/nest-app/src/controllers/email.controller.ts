import {
    Body,
    Controller,
    Post,
    BadRequestException,
    NotFoundException,
  } from '@nestjs/common';
  import { EmailService } from '../services/email.service';
  import { SendEmailDto } from '../dto/send-email.dto';
  import { VerifyEmailDto } from '../dto/verify-email.dto';
  import { VerifyCodeDto } from '../dto/verify-code.dto';

  @Controller('email')
  export class EmailController {
    constructor(private readonly emailService: EmailService) {}

    @Post('send-authentication')
    async sendAuthentication(@Body() dto: SendEmailDto) {
      return await this.emailService.sendAuthenticationEmail(dto.username);
    }

    @Post('verify-email')
    async verifyEmail(@Body() dto: VerifyEmailDto) {
      return await this.emailService.sendEmailVerification(dto.username);
    }

    @Post('verify-code')
    async verifyCode(@Body() dto: VerifyCodeDto) {
      return await this.emailService.sendEmailCode(dto.username, dto.verificationCode);
    }

    @Post('request-bind-email')
    async requestRebindEmail(@Body() dto: SendEmailDto) {
      return await this.emailService.sendRebindRequestEmail(dto.username);
    }
  }
