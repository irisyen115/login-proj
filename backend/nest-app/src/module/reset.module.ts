import { Module } from '@nestjs/common';
import { SequelizeModule } from '@nestjs/sequelize';
import { PasswordVerify } from '../models/password-verify.models';
import { User } from '../models/user.models';
import { ResetService } from '../services/reset.service';
import { ResetController } from '../controllers/reset.controller';

@Module({
  imports: [SequelizeModule.forFeature([PasswordVerify, User])],
  controllers: [ResetController],
  providers: [ResetService],
  exports: [ResetService],
})
export class ResetModule {}
