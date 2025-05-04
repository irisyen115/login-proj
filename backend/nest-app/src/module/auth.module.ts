import { Module } from '@nestjs/common';
import { AuthService } from '../services/auth.service';
import { AuthController } from '../controllers/auth.controllers';
import { UserModule } from './user.module';
import { RedisModule } from '../module/redis.module';
import { ConfigModule } from '@nestjs/config';

@Module({
  imports: [UserModule, RedisModule, ConfigModule],
  controllers: [AuthController],
  providers: [AuthService],
})
export class AuthModule {}
