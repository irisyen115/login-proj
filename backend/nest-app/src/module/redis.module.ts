import { Module, Global } from '@nestjs/common';
import { ConfigService, ConfigModule } from '@nestjs/config';
import { RedisService } from '../services/redis.service';
import { createClient } from 'redis';

@Global()
@Module({
  imports: [ConfigModule],
  providers: [
    {
      provide: 'REDIS_CLIENT',
      useFactory: async (configService: ConfigService) => {
        const host = configService.get('REDIS_HOST');
        const port = parseInt(configService.get('REDIS_PORT') || '10');
        const client = createClient({
          socket: {
            host,
            port,
          },
        });
        client.on('error', err => console.error('Redis error', err));

        await client.connect();

        return client;
      },
      inject: [ConfigService],
    },
    RedisService,
  ],
  exports: ['REDIS_CLIENT', RedisService],
})
export class RedisModule {}
