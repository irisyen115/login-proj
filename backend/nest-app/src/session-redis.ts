import { createClient } from 'redis';

export const sessionRedisClient = createClient({
  socket: {
    host: process.env.REDIS_HOST,
    port: parseInt(process.env.REDIS_PORT || '6379'),
  },
  legacyMode: true,
} as any);
sessionRedisClient.on('error', err => console.error('Redis error', err));
sessionRedisClient.on('connect', () => {
  console.log('Redis client connected');
});

sessionRedisClient.connect().catch(console.error);
