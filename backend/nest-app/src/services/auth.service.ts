import {
  Injectable,
  UnauthorizedException,
  BadRequestException,
  InternalServerErrorException,
} from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { User } from '../models/user.models';
import { LineBindingUser } from '../models/line-binding-user.models';
import { RedisService } from '../common/utils/redis.util';
import axios from 'axios';
import { OAuth2Client } from 'google-auth-library';
import { EmailService } from './email.service';
import * as bcrypt from 'bcrypt';

@Injectable()
export class AuthService {
  private readonly client: OAuth2Client;

  constructor(
    private configService: ConfigService,
    private readonly emailService: EmailService,
    @InjectRepository(User) private userRepo: Repository<User>,
    @InjectRepository(LineBindingUser) private bindingRepo: Repository<LineBindingUser>,
    private readonly redisService: RedisService
  ) {
    this.client = new OAuth2Client(this.configService.get('GOOGLE_CLIENT_ID'));
  }

  async updateLoginCacheState(uid: string) {
    const client = this.redisService.getClient();
    const key = `user:${uid}`;
    const cached = await client.get(key);

    if (cached) {
      const userData = JSON.parse(cached);
      userData.last_login = new Date().toISOString();
      userData.login_count += 1;
      await client.set(key, JSON.stringify(userData), 'EX', 3600);
    } else {
      const user = await this.userRepo.findOne({ where: { id: Number(uid) } });
      if (user) {
        await client.set(key, JSON.stringify(user), 'EX', 3600);
      }
    }
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
      const picture = payload.picture;
      if (!email) throw new BadRequestException('無法取得使用者的 email');

      let user = await this.userRepo.findOne({ where: { email } });
      if (!user) {
        user = this.userRepo.create({
          email,
          username: payload.name,
        });
      }

      if (picture) {
        const res = await axios.get(picture, { responseType: 'arraybuffer' });
        const filename = `${user.id}.jpg`;
        const filePath = `${this.configService.get('UPLOAD_FOLDER')}/${filename}`;
        require('fs').writeFileSync(filePath, res.data);

        user.profileImage = filePath;
        user.pictureName = filename;
      }

      await this.updateLoginCacheState(user.id.toString());
      user.lastLogin = new Date();
      user.loginCount = (user.loginCount || 0) + 1;
      await this.userRepo.save(user);

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

    const binding = this.bindingRepo.create({ userId: user.id, lineId: lineUid });
    await this.bindingRepo.save(binding);

    const emailSent = await this.emailService.triggerEmail(
      `${this.configService.get('IRIS_DS_SERVER_URL')}/send-mail`,
      user.email,
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
        const newUser = this.userRepo.create({
          email,
          username: googleUser.name,
          profileImage: googleUser.picture,
        });
        await this.userRepo.save(newUser);
        return newUser;
      }
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
