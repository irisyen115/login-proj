import { Module } from '@nestjs/common';
<<<<<<< HEAD
import { AppController } from './app.controller';
import { AppService } from './app.service';

@Module({
  imports: [],
  controllers: [AppController],
  providers: [AppService],
})
export class AppModule {}
=======
import { ConfigModule, ConfigService } from '@nestjs/config';
import { SequelizeModule } from '@nestjs/sequelize';
import { AuthModule } from './module/auth.module';
import { UserModule } from './module/user.module';
import { ResetModule } from './module/reset.module';
import { WebhookModule } from './module/webhook.module';
import { EmailModule } from './module/email.module';
import { RedisModule } from './module/redis.module';
import { FileModule } from './module/file.module';
import { User } from './models/user.models';
import { EmailVerify } from './models/email-verify.models';
import { PasswordVerify } from './models/password-verify.models';
import { LineBindingUser } from './models/line-binding-user.models';
import { SessionMiddleware } from './middleware/session.middleware';
import { NestModule, MiddlewareConsumer } from '@nestjs/common';

@Module({
  imports: [
    ConfigModule.forRoot({
      isGlobal: true,
      envFilePath: '.env',
    }),
    SequelizeModule.forRootAsync({
      useFactory: async (configService: ConfigService) => {
        const databaseUrl = configService.get<string>('DATABASE_URL');
        if (!databaseUrl) {
          throw new Error('DATABASE_URL is not defined in the environment variables');
        }
        const parsedUrl = new URL(databaseUrl);
        console.log('Parsed URL:', parsedUrl);

        return {
          dialect: 'postgres',
          host: parsedUrl.hostname,
          port: parseInt(parsedUrl.port),
          username: parsedUrl.username,
          password: parsedUrl.password,
          database: parsedUrl.pathname.slice(1),
          models: [User, EmailVerify, PasswordVerify, LineBindingUser],
          autoLoadModels: true,
          synchronize: true,
        };
      },
      inject: [ConfigService],
    }),
    AuthModule,
    UserModule,
    ResetModule,
    WebhookModule,
    EmailModule,
    RedisModule,
    FileModule,
  ],
})
export class AppModule implements NestModule {
  configure(consumer: MiddlewareConsumer) {
    consumer
      .apply(SessionMiddleware)
      .forRoutes('*');
  }
}
>>>>>>> 99ee142e (Setting up session login using node.js #119)
