import {
  Controller,
  Post,
  Get,
  UploadedFile,
  UseInterceptors,
  Req,
  Res,
  HttpException,
  HttpStatus,
  Logger,
} from '@nestjs/common';
import { FileInterceptor } from '@nestjs/platform-express';
import { Request, Response } from 'express';
import { FileService } from '../services/file.service';
import { ConfigService } from '@nestjs/config';

@Controller()
export class FileController {
  private readonly logger = new Logger(FileController.name);
  constructor(
    private readonly fileService: FileService,
    private readonly configService: ConfigService,
  ) {}
  @Post('upload-avatar')
  @UseInterceptors(FileInterceptor('file'))
  async uploadAvatar(
    @UploadedFile() file: Express.Multer.File,
    @Req() req: Request
  ) {
    const userId = (req as any).userId;
    if (!file) {
      throw new HttpException('請提供照片', HttpStatus.BAD_REQUEST);
    }

    if (!userId) {
      throw new HttpException('未授權', HttpStatus.UNAUTHORIZED);
    }

    try {
      const avatarUrl = await this.fileService.saveUserAvatar(userId, file);
      return {
        message: '照片上傳成功',
        avatar_url: avatarUrl,
      };
    } catch (e) {
      throw new HttpException(
        `照片上傳錯誤: ${e.message}`,
        HttpStatus.INTERNAL_SERVER_ERROR,
      );
    }
  }

  @Get('get_user_image')
  async getUserImage(@Req() req: Request, @Res() res: Response) {
    const userId = (req as any).userId;

    if (!userId) {
      throw new HttpException('未授權', HttpStatus.UNAUTHORIZED);
    }

    const pictureName = await this.fileService.getUserImage(userId);
    if (!pictureName) {
      throw new HttpException('無圖片可顯示', HttpStatus.NOT_FOUND);
    }

    const uploadFolder = this.configService.get<string>('UPLOAD_FOLDER');

    try {
      return res.sendFile(pictureName, { root: uploadFolder });
    } catch (e) {
      throw new HttpException(
        `檔案讀取錯誤: ${e.message}`,
        HttpStatus.INTERNAL_SERVER_ERROR,
      );
    }
  }
}
