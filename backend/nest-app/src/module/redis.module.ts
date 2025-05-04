import { Module } from '@nestjs/common';
import { RedisService } from '../common/utils/redis.util';

@Module({
  providers: [RedisService],
  exports: [RedisService],
})
export class RedisModule {}
