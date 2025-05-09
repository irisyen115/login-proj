import { forwardRef, Module } from '@nestjs/common';
import { SequelizeModule } from '@nestjs/sequelize';
import { UserController } from '../controllers/user.controller';
import { UserService } from '../services/user.service';
import { User } from '../models/user.models';
import { ConfigModule } from '@nestjs/config';
import { RedisModule } from './redis.module';
import { AuthModule } from './auth.module';

@Module({
  imports: [
    forwardRef(() => AuthModule),
    RedisModule,
    SequelizeModule.forFeature([User]),
    ConfigModule,
  ],
  controllers: [UserController],
  providers: [UserService],
  exports: [UserService],
})
export class UserModule {}
