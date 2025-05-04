import {
    Controller,
    Post,
    UseInterceptors,
    UploadedFile,
    Req,
    Res,
    Get,
    UnauthorizedException,
    NotFoundException,
    InternalServerErrorException,
  } from '@nestjs/common';
  import { FileInterceptor } from '@nestjs/platform-express';
  import { Request, Response } from 'express';
  import { FileService } from '../services/file.service';
  import { UserService } from '../services/user.service';
  import { diskStorage } from 'multer';
  import { extname, join } from 'path';
  import { ConfigService } from '@nestjs/config';

  @Controller('file')
  export class FileController {
    constructor(
      private readonly fileService: FileService,
      private readonly userService: UserService,
      private readonly configService: ConfigService,
    ) {}

    @Post('upload-avatar')
    @UseInterceptors(FileInterceptor('file', {
      storage: diskStorage({
        destination: './uploads',
        filename: (req, file, cb) => {
          const userId = req.user?.id;
          const ext = extname(file.originalname);
          cb(null, `${userId}${ext}`);
        },
      }),
    }))
    async uploadAvatar(
      @UploadedFile() file: Express.Multer.File,
      @Req() req: Request,
      @Res() res: Response,
    ) {
      const userId = req.user?.id;
      if (!userId) throw new UnauthorizedException('未授權');

      if (!file) return res.status(400).json({ error: '請提供照片' });

      try {
        const avatarUrl = await this.fileService.saveUserAvatar(userId, file);
        return res.json({ message: '照片上傳成功', avatar_url: avatarUrl });
      } catch (err) {
        throw new InternalServerErrorException(`照片上傳錯誤: ${err.message}`);
      }
    }

    @Get('get_user_image')
    async getUserImage(@Req() req: Request, @Res() res: Response) {
      const userId = req.user?.id;
      if (!userId) throw new UnauthorizedException('未授權');

      const user = await this.userService.getUserById(userId);
      if (!user) throw new NotFoundException('用戶未找到');

      const pictureName = await this.fileService.getUserImage(user.id);
      if (!pictureName) return res.status(404).json({ error: '無圖片可顯示' });

      const uploadPath = this.configService.get<string>('UPLOAD_FOLDER') || './uploads';
      return res.sendFile(join(uploadPath, pictureName));
    }
  }
