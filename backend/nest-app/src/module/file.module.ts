import { Module } from '@nestjs/common';
import { FileController } from '../controllers/file.controller';
import { FileService } from '../services/file.service';
import { SequelizeModule } from '@nestjs/sequelize';
import { User } from '../models/user.models';
import { UserModule } from './user.module';
import { ConfigModule } from '@nestjs/config';

@Module({
  imports: [
    SequelizeModule.forFeature([User]),
    UserModule,
    ConfigModule,
  ],
  controllers: [FileController],
  providers: [FileService],
})
export class FileModule {}
