import { Module } from '@nestjs/common';
import { SequelizeModule } from '@nestjs/sequelize';
import { EmailController } from '../controllers/email.controller';
import { EmailService } from '../services/email.service';
import { User } from '../models/user.models';
import { EmailVerify } from '../models/email-verify.models';
import { PasswordVerify } from '../models/password-verify.models';
import { ConfigModule } from '@nestjs/config';

@Module({
  imports: [
    ConfigModule,
    SequelizeModule.forFeature([User, EmailVerify, PasswordVerify]),
  ],
  controllers: [EmailController],
  providers: [EmailService],
  exports: [EmailService],
})
export class EmailModule {}
