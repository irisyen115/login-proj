import { Injectable } from '@nestjs/common';
import Redis from 'ioredis';

@Injectable()
export class RedisService {
  private client: Redis;

  constructor() {
    this.client = new Redis({
      host: process.env.REDIS_HOST || 'localhost',
      port: Number(process.env.REDIS_PORT) || 6379,
    });
  }

  getClient(): Redis {
    return this.client;
  }

  async get(key: string): Promise<string | null> {
    return await this.client.get(key);
  }

  async setex(key: string, seconds: number, value: string): Promise<void> {
    await this.client.setex(key, seconds, value);
  }

  async updateLoginCache(uid: number) {
    const key = `user:${uid}`;
    try {
      const cached = await this.client.get(key);
      if (cached) {
        const userData = JSON.parse(cached);
        userData.last_login = new Date().toISOString();
        userData.login_count += 1;
        await this.client.setex(key, 3600, JSON.stringify(userData));
      }
    } catch (err) {
      console.error(`Redis error for key ${key}:`, err);
    }
  }
}
