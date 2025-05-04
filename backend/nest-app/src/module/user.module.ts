import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { UserController } from '../controllers/user.controller';
import { UserService } from '../services/user.service';
import { User } from '../models/user.models';
import { ConfigModule } from '@nestjs/config';
import { RedisService } from '../common/utils/redis.util';

@Module({
  imports: [
    TypeOrmModule.forFeature([User]),
    ConfigModule,
  ],
  controllers: [UserController],
  providers: [UserService, RedisService],
  exports: [UserService],
})
export class UserModule {}
