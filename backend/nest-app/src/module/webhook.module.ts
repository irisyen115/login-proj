import { Module } from '@nestjs/common';
import { WebhookController } from '../controllers/webhook.controller';
import { WebhookService } from '../services/webhook.service';
import { AuthModule } from '../module/auth.module';
import { ConfigModule } from '@nestjs/config';
import { UserModule } from '../module/user.module';

@Module({
  imports: [
    ConfigModule,
    AuthModule,
    UserModule,
  ],
  controllers: [WebhookController],
  providers: [WebhookService],
})
export class WebhookModule {}
