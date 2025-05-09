import {
  Injectable,
  UnauthorizedException,
  BadRequestException,
  InternalServerErrorException,
  Inject,
  forwardRef,
  Logger,
} from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { InjectModel } from '@nestjs/sequelize';
import { User } from '../models/user.models';
import { LineBindingUser } from '../models/line-binding-user.models';
import { RedisService } from '../services/redis.service';
import { UserService } from './user.service';
import axios from 'axios';
import { OAuth2Client } from 'google-auth-library';
import { EmailService } from './email.service';
import * as bcrypt from 'bcryptjs';
import * as fs from 'fs';
import e from 'express';

@Injectable()
export class AuthService {
  private readonly client: OAuth2Client;
  private readonly logger = new Logger(AuthService.name);

  constructor(
    private configService: ConfigService,
    private readonly emailService: EmailService,
    @Inject(forwardRef(() => UserService))
    private userService: UserService,
    @InjectModel(User) private userRepo: typeof User,
    @InjectModel(LineBindingUser) private bindingRepo: typeof LineBindingUser,
    private readonly redisService: RedisService
  ) {
    this.client = new OAuth2Client(this.configService.get('GOOGLE_CLIENT_ID'));
  }

  async authenticateGoogleUser(idToken: string) {
    try {
      const ticket = await this.client.verifyIdToken({
        idToken,
        audience: this.configService.get('GOOGLE_CLIENT_ID'),
      });

      const payload = ticket.getPayload();
      if (!payload) throw new UnauthorizedException('無法驗證 Google 使用者');

      const email = payload.email;
      if (!email) throw new BadRequestException('無法取得使用者的 email');

      if (!payload.name) {
        throw new BadRequestException('Google 資料缺少使用者名稱');
      }

      const picture = payload.picture;

      let user = await this.userRepo.findOne({ where: { email } });

      if (!user) {
        user = this.userRepo.build({
          email,
          username: payload.name,
        } as User);
        await user.save();
      }

      if (picture) {
        const filePath = `${this.configService.get('UPLOAD_FOLDER')}/${user.id}.jpg`;

        if (!fs.existsSync(filePath)) {
          const res = await axios.get(picture, { responseType: 'arraybuffer' });
          fs.writeFileSync(filePath, res.data);

          user.profileImage = filePath;
          user.pictureName = `${user.id}.jpg`;
        } else {
          user.profileImage = filePath;
        }
      }

      await this.userService.updateLoginCacheState(user.id);
      user.updateLastLogin();
      await user.save();

      const sessionId = this.userService.generateSignedSessionId(user.id);
      await this.redisService.set(sessionId, user.id.toString(), 1800);

      return user;
    } catch (err) {
      throw new InternalServerErrorException(err.message);
    }
  }

  async bindLineUidToUser(lineUid: string, user: User) {
    if (!user) throw new BadRequestException('帳號不存在');

    const existingBinding = await this.bindingRepo.findOne({ where: { userId: user.id } });
    if (existingBinding) {
      throw new BadRequestException(`已綁定 ${user.email} 信箱`);
    }

    const binding = await this.bindingRepo.create({ userId: user.id, lineId: lineUid });
    if (!binding) {
      throw new InternalServerErrorException('綁定失敗');
    }

    const emailSent = await this.emailService.triggerEmail(
      user.email,
      '帳戶綁定確認',
      '帳戶綁定確認,您的 Line 已綁定此 Email！'
    );

    if (!emailSent) {
      throw new InternalServerErrorException('Email 發送失敗');
    }

    return {
      message: '綁定成功，請檢查您的 Email',
      username: user.username,
      role: user.role,
      last_login: user.lastLogin,
      login_count: user.loginCount,
    };
  }

  async identifyGoogleUserByToken(userData: any): Promise<User> {
    const { google_token, username, password = '' } = userData;

    if (google_token) {
      const googleUser = await this.verifyGoogleToken(google_token);
      if (!googleUser) {
        throw new BadRequestException('Google 驗證失敗');
      }

      const email = googleUser.email;
      const user = await this.userRepo.findOne({ where: { email } });
      if (!user) {
        const newUser = new User({
          email,
          username: googleUser.name,
          profileImage: googleUser.picture,
        } as User);
        await newUser.save();
        return newUser;
      }

      const sessionId = this.userService.generateSignedSessionId(user.id);
      await this.redisService.set(sessionId, user.id.toString(), 1800);

      await this.userService.updateLoginCacheState(user.id);
      user.updateLastLogin();
      await user.save();

      return user;
    } else {
      const user = await this.userRepo.findOne({ where: { username } });
      if (!user || !(await bcrypt.compare(password, user.passwordHash))) {
        throw new BadRequestException('密碼錯誤');
      }
      return user;
    }
  }

  async verifyGoogleToken(token: string) {
    try {
      const ticket = await this.client.verifyIdToken({
        idToken: token,
        audience: this.configService.get('GOOGLE_CLIENT_ID'),
      });
      const payload = ticket.getPayload();
      if (!payload) {
        throw new UnauthorizedException('無法驗證 Google 使用者');
      }
      if (
        !['accounts.google.com', 'https://accounts.google.com'].includes(payload.iss)
      ) {
        return null;
      }
      return {
        email: payload.email,
        name: payload.name,
        picture: payload.picture,
      };
    } catch (err) {
      return null;
    }
  }
}
