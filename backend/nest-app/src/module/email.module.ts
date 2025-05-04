import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { EmailController } from '../controllers/email.controller';
import { EmailService } from '../services/email.service';
import { User } from '../models/user.models';
import { EmailVerify } from '../models/email-verify.models';
import { PasswordVerify } from '../models/password-verify.models';
import { ConfigModule } from '@nestjs/config';

@Module({
  imports: [
    ConfigModule, // 用來注入環境變數
    TypeOrmModule.forFeature([User, EmailVerify, PasswordVerify]), // 注入使用到的 Entity
  ],
  controllers: [EmailController],
  providers: [EmailService],
  exports: [EmailService], // 如果其他 Module 也需要用 EmailService 可以 export
})
export class EmailModule {}
