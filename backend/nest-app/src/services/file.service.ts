import { Injectable, NotFoundException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { User } from '../models/user.models';
import { ConfigService } from '@nestjs/config';
import * as fs from 'fs';
import * as path from 'path';

@Injectable()
export class FileService {
  constructor(
    @InjectRepository(User)
    private usersRepository: Repository<User>,
    private configService: ConfigService,
  ) {}

  async saveUserAvatar(userId: number, file: Express.Multer.File): Promise<string> {
    const uploadFolder = this.configService.get<string>('UPLOAD_FOLDER');
    const filename = `${userId}.jpg`;
    if (!uploadFolder) {
      throw new Error('UPLOAD_FOLDER is not defined in Config');
    }
    const filepath = path.join(uploadFolder, filename);

    fs.writeFileSync(filepath, file.buffer);

    const user = await this.usersRepository.findOneBy({ id: userId });
    if (!user) throw new NotFoundException('User not found');

    user.profileImage = filepath;
    user.pictureName = filename;
    await this.usersRepository.save(user);

    return filepath;
  }

  async getUserImage(userId: number): Promise<string | null> {
    const user = await this.usersRepository.findOneBy({ id: userId });
    const uploadFolder = this.configService.get<string>('UPLOAD_FOLDER');
    if (!uploadFolder) {
      throw new Error('UPLOAD_FOLDER is not defined in Config');
    }
    if (!user) throw new NotFoundException('User not found');
    if (user?.profileImage) {
      const imagePath = path.join(uploadFolder, user.pictureName);
      if (fs.existsSync(imagePath)) {
        return user.pictureName;
      }
    }
    return null;
  }
}
