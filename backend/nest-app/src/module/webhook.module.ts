import { Module } from '@nestjs/common';
import { WebhookController } from '../controllers/webhook.controller';
import { WebhookService } from '../services/webhook.service';
import { AuthModule } from '../module/auth.module';
import { ConfigModule } from '@nestjs/config';

@Module({
  imports: [
    ConfigModule,
    AuthModule,
  ],
  controllers: [WebhookController],
  providers: [WebhookService],
})
export class WebhookModule {}
