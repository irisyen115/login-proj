import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import cookieParser from 'cookie-parser';
import * as fs from 'fs';
import { ConfigService } from '@nestjs/config';
import cors from 'cors';
import session from 'express-session';
import { RedisStore } from 'connect-redis';
import { sessionRedisClient } from './session-redis';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  const configService = app.get(ConfigService);

  app.use(cookieParser());
  app.enableCors({
    origin: app.get(ConfigService).get('IRIS_DS_SERVER_URL'),
    credentials: true,
  });

  const uploadFolder = app.get(ConfigService).get('UPLOAD_FOLDER');
  if (!fs.existsSync(uploadFolder)) {
    fs.mkdirSync(uploadFolder, { recursive: true });
  }

  app.use(
    session({
      store: new RedisStore({
        client: sessionRedisClient,
        ttl: 1800,
      }),
      secret: 'your-secret-key',
      resave: false,
      saveUninitialized: false,
      cookie: {
        maxAge: 1800000,
      },
    }),
  );



  app.use(cors({
    origin: configService.get('IRIS_DS_SERVER_URL'),
    credentials: true,
  }));

  await app.listen(5000, '0.0.0.0');
}
bootstrap();
