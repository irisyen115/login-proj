import { forwardRef, Module } from '@nestjs/common';
import { SequelizeModule } from '@nestjs/sequelize';
import { AuthService } from '../services/auth.service';
import { AuthController } from '../controllers/auth.controllers';
import { UserModule } from './user.module';
import { RedisModule } from '../module/redis.module';
import { ConfigModule } from '@nestjs/config';
import { EmailModule } from './email.module';
import { User } from '../models/user.models';
import { LineBindingUser } from '../models/line-binding-user.models';
import { EmailVerify } from '../models/email-verify.models';
import { PasswordVerify } from '../models/password-verify.models';

@Module({
  imports: [
    forwardRef(() => UserModule),
    SequelizeModule.forFeature([User, LineBindingUser, EmailVerify, PasswordVerify]),
    EmailModule,
    RedisModule,
    ConfigModule
  ],
  controllers: [AuthController],
  providers: [AuthService],
  exports: [AuthService],
})
export class AuthModule {}
