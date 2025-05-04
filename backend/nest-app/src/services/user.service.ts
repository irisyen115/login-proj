import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { User } from '../models/user.models';
import { RegisterUserDto } from '../dto/register-user.dto';
import { LoginUserDto } from '../dto/login-user.dto';
import { AuthService } from './auth.service';
import { RedisService } from '../common/utils/redis.util';
import Redis from 'ioredis';

@Injectable()
export class UserService {
  private redisClient: Redis;

  constructor(
    @InjectRepository(User)
    private userRepository: Repository<User>,
    private redisService: RedisService,
    private authService: AuthService,
  ) {
    this.redisClient = this.redisService.getClient();
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

    const newUser = this.userRepository.create({ username, email, passwordHash: password });
    await this.userRepository.save(newUser);

    return { user: newUser, role: 'user' };
  }

  async loginUser(data: LoginUserDto) {
    const { username, password } = data;

    if (!username || !password) {
      return { error: '請提供帳號和密碼' };
    }

    const user = await this.userRepository.findOne({ where: { username } });
    if (!user || user.passwordHash !== password) {
      return { error: '帳號或密碼錯誤' };
    }

    await this.authService.updateLoginCacheState(user.id.toString());

    user.lastLogin = new Date();
    user.loginCount = (user.loginCount || 0) + 1;
    await this.userRepository.save(user);

    return {
      user_id: user.id,
      role: user.role,
      last_login: user.lastLogin,
      login_count: user.loginCount,
    };
  }


  async fetchUsersData(userId: number) {
    const user = await this.getUserById(userId);
    if (!user) return { error: '使用者不存在' };

    if (user.role === 'admin') {
      const users = await this.userRepository.find({
        select: ['id', 'username', 'lastLogin', 'loginCount', 'role'],
      });
      return users;
    } else if (user.role === 'user') {
      const userData = {
        id: user.id,
        username: user.username,
        lastLogin: user.lastLogin,
        loginCount: user.loginCount,
        role: user.role,
      };
      return [userData];
    }
    return { error: '未知的角色' };
  }

  private getUserKey(uid: number): string {
    return `user:${uid}`;
  }

  async getUserById(uid: number): Promise<User | null> {
    if (!uid) return null;
    const cacheKey = this.getUserKey(uid);
    const cachedUser = await this.redisClient.get(cacheKey);
    if (cachedUser) {
      return JSON.parse(cachedUser);
    }

    const user = await this.userRepository.findOne({ where: { id: uid } });
    if (user) {
      await this.redisClient.setex(cacheKey, 3600, JSON.stringify(user));
    }
    return user;
  }
}