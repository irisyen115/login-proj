import { Injectable, Inject, forwardRef, Logger } from '@nestjs/common';
import { InjectModel } from '@nestjs/sequelize';
import { User } from '../models/user.models';
import { RegisterUserDto } from '../dto/register-user.dto';
import { LoginUserDto } from '../dto/login-user.dto';
import { AuthService } from './auth.service';
import { RedisService } from '../services/redis.service';
import { ConfigService } from '@nestjs/config';
import { RedisClientType } from 'redis';
import { v4 as uuidv4 } from 'uuid';
import * as hmac from 'crypto';
import base64url from 'base64url';

@Injectable()
export class UserService {
  private redisClient: RedisClientType;
  private readonly secretKey: string;
  private readonly logger = new Logger(UserService.name);
  constructor(
    @InjectModel(User)
    private userRepository: typeof User,
    private redisService: RedisService,
    @Inject(forwardRef(() => AuthService))
    private authService: AuthService,
    private readonly configService: ConfigService,
  ) {
    this.redisClient = this.redisService.getClient();
    this.secretKey = this.configService.get<string>('SECRET_KEY') ?? '';
  }

  async registerUser(data: RegisterUserDto) {
    const { username, email, password } = data;

    if (!username || !email || !password) {
      return { error: '請提供帳號、密碼和電子郵件' };
    }

    const existing = await this.userRepository.findOne({ where: { email } });
    if (existing) {
      return { error: '帳號已存在' };
    }

    const newUser = await this.userRepository.create({
      username : username,
      email : email,
    } as User);
    if (!newUser) {
      return { error: '註冊失敗' };
    }
    await newUser.setPassword(password);
    await newUser.save();
    return {
      status: 'success',
      user: {
        id: newUser.id,
        username: newUser.username,
        email: newUser.email,
      },
      role: 'user',
    };
  }

  async loginUser(data: LoginUserDto) {

    const { username, password } = data;

    if (!username || !password) {
      return { error: '請提供帳號和密碼' };
    }

    const user = await this.userRepository.findOne({ where: { username } });
    if (!user || !(await user.checkPassword(password))) {
      return { error: '帳號或密碼錯誤' };
    }

    await this.updateLoginCacheState(user.id);

    user.updateLastLogin();

    await user.save();
    return {
      status: 'success',
      user: {
        id: user.id,
        username: user.username,
        email: user.email,
        lastLogin: user.lastLogin,
        loginCount: user.loginCount,
      },
      role: user.role,
    };
    }

    async fetchUsersData(userId: number) {
      if (!userId) {
        return { error: '請提供使用者ID' };
      }

      const user = await this.getUserById(userId);
      if (!user) {
        return { error: '使用者不存在' };
      }

      if (user.role === 'admin') {
        const users = await this.userRepository.findAll();
        const usersData = users.map((user) => ({
          id: user.id,
          username: user.username,
          last_login: user.lastLogin ? new Date(user.lastLogin) : "無登入記錄",
          login_count: Number(user.loginCount) || 0,
          role: user.role,
        }));

        return usersData;

      } else if (user.role === 'user') {
        const userData = {
          id: user.id,
          username: user.username,
          last_login: user.lastLogin ? new Date(user.lastLogin) : "無登入記錄",
          login_count: user.loginCount || 0,
          role: user.role,
        };

        return [userData];

      } else {
        return { error: '未知的角色' };
      }
    }

  private getUserKey(uid: number): string {
    return `user:${uid}`;
  }

  async getUserById(uid: number): Promise<User | null> {
    if (!uid) return null;

    const cacheKey = this.getUserKey(uid);
    const cachedUser = await this.redisClient.get(cacheKey);
    if (cachedUser) {
      const plain = JSON.parse(cachedUser);
      const rawUser = plain.dataValues ?? plain;
      const userInstance = User.fromJson(rawUser);

      return userInstance;
    }

    const user = await this.userRepository.findOne({ where: { id: uid } });
    if (user) {
      await this.redisClient.set(cacheKey, JSON.stringify(user.toJSON()));
    }
    return user;
}


async updateLoginCacheState(uid: number) {
  try {
    const cached = await this.redisService.get(this.getUserKey(uid));
    let user: any;
    if (cached) {
      const parsed = JSON.parse(cached);
      const rawUser = parsed.dataValues ?? parsed;

      const currentCount = Number(rawUser.loginCount) || 0;
      rawUser.loginCount = currentCount + 1;
      rawUser.lastLogin = new Date();

      user = User.fromJson(rawUser);

      await this.redisService.set(this.getUserKey(uid), JSON.stringify(user));
      await user.updateLastLogin();
    } else {
      user = await this.userRepository.findByPk(uid);
      if (user) {
        user.loginCount += 1;
        user.lastLogin = new Date();
        await user.save();

        await this.redisService.set(this.getUserKey(uid), JSON.stringify(user));
      }
    }
  } catch (error) {
    this.logger.error('更新 login 快取狀態失敗', error);
  }
}

generateSignedSessionId(userId: number): string {
    const rawSessionId = uuidv4();
    const message = `${userId}:${rawSessionId}`;
    const signature = hmac.createHmac('sha256', this.secretKey).update(message).digest();
    const signed = base64url.encode(`${message}.${signature.toString('base64')}`);
    return signed;
  }

}