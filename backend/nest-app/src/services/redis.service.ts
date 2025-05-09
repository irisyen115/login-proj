import { Injectable, Inject } from '@nestjs/common';
import { RedisClientType } from 'redis';
import { REDIS_CLIENT } from '../module/redisClient.module';

@Injectable()
export class RedisService {
  constructor(
    @Inject(REDIS_CLIENT) private readonly redisClient: RedisClientType
) {}

  async get(key: string): Promise<string | null> {
    return await this.redisClient.get(key);
  }

  async set(key: string, value: string, ex: number = 3600): Promise<void> {
    await this.redisClient.set(key, value, { EX: ex });
  }

  async setSession(sessionId: string, userId: string, ex: number = 1800): Promise<void> {
    await this.redisClient.set(sessionId, userId, { EX: ex });
  }

  async expire(key: string, ttl: number): Promise<void> {
    await this.redisClient.expire(key, ttl);
  }

  async del(key: string): Promise<void> {
    await this.redisClient.del(key);
  }

  getClient(): RedisClientType  {
    return this.redisClient;
  }
}
