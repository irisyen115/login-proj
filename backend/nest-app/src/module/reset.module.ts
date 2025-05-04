import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { PasswordVerify } from '../models/password-verify.models';
import { User } from '../models/user.models';
import { ResetService } from '../services/reset.service';

@Module({
  imports: [TypeOrmModule.forFeature([PasswordVerify, User])],
  providers: [ResetService],
})
export class ResetModule {}
