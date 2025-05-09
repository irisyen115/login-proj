import { Injectable, NotFoundException, BadRequestException } from '@nestjs/common';
import { InjectModel } from '@nestjs/sequelize';
import { User } from '../models/user.models';
import { EmailVerify } from '../models/email-verify.models';
import { PasswordVerify } from '../models/password-verify.models';
import { ConfigService } from '@nestjs/config';
import axios from 'axios';
import { Logger } from '@nestjs/common';

@Injectable()
export class EmailService {
  private readonly logger = new Logger(EmailService.name);
  constructor(
    @InjectModel(User)
    private userRepo: typeof User,
    @InjectModel(EmailVerify)
    private emailVerifyRepo: typeof EmailVerify,
    @InjectModel(PasswordVerify)
    private passwordVerifyRepo: typeof PasswordVerify,
    private configService: ConfigService,
  ) {}

  private generateCode(length: number): string {
    const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let result = '';
    for (let i = 0; i < length; i++) {
      result += characters.charAt(Math.floor(Math.random() * characters.length));
    }
    return result;
  }

  async triggerEmail(to: string, subject: string, body: string) {
    const url = `${this.configService.get('IRIS_DS_SERVER_URL')}/send-mail`;
    try {
      const response = await axios.post(url, {
        recipient: to,
        subject,
        body,
      });
      return response.data;
    } catch (error) {
      console.error('Email 發送失敗:', error.response || error.message);
      throw new BadRequestException('Email 發送失敗');
    }
  }

  async sendEmailVerification(username: string) {
    const user = await this.userRepo.findOne({ where: { username } });
    if (!user) throw new NotFoundException('用戶不存在');
    if (!user.email) throw new BadRequestException('未綁定 Email');

    try {
      const existing = await this.emailVerifyRepo.findOne({
        where: { userId: user.id },
        order: [['validUntil', 'DESC']],
      });

      if (existing && new Date() <= existing.validUntil) {
        return { message: '驗證碼已發送，請勿重複點取' };
      }

      const code = this.generateCode(6);
      await this.emailVerifyRepo.create({
        emailVerifyCode: code,
        validUntil: new Date(Date.now() + 15 * 60 * 1000),
        userId: user.id,
      });

      await this.triggerEmail(user.email, '帳戶綁定確認', code);
      return { message: '驗證碼已發送，請檢查電子郵件' };
    } catch (error) {
      console.error('發送電子郵件驗證碼時發生錯誤:', error.message);
      throw new BadRequestException('發送電子郵件驗證碼時發生錯誤');
    }
  }

  async sendAuthenticationEmail(username: string) {
    const user = await this.userRepo.findOne({ where: { username } });
    if (!user) throw new NotFoundException('用戶不存在');
    if (!user.email) throw new BadRequestException('用戶未綁定 Email');

    const existing = await this.passwordVerifyRepo.findOne({
      where: { userId: user.id },
      order: [['validUntil', 'DESC']],
    });

    if (existing && new Date() <= existing.validUntil) {
      return { message: '驗證碼已發送，請勿重複點取' };
    }

    const code = this.generateCode(30);
    await this.passwordVerifyRepo.create({
      passwordVerifyCode: code,
      validUntil: new Date(Date.now() + 15 * 60 * 1000),
      userId: user.id,
    } as PasswordVerify);

    const link = `${this.configService.get('IRIS_DS_SERVER_URL')}/reset-password/${code}`;
    await this.triggerEmail(user.email, '帳戶綁定確認', link);
    return { message: '驗證信已發送，請重新設置' };
  }

  async sendEmailCode(username: string, code: string) {
    const user = await this.userRepo.findOne({ where: { username } });
    if (!user) throw new NotFoundException('用戶不存在');

    const record = await this.emailVerifyRepo.findOne({
      where: { userId: user.id },
      order: [['validUntil', 'DESC']],
    });

    if (!record || record.emailVerifyCode !== code) {
      throw new BadRequestException('驗證碼錯誤');
    }
    if (new Date() > record.validUntil) {
      throw new BadRequestException('驗證碼已過期');
    }

    return { message: '驗證成功，Email 已驗證' };
  }

  async sendRebindRequestEmail(username: string) {
    const user = await this.userRepo.findOne({ where: { username } });
    if (!user) throw new NotFoundException('找不到使用者');

    const body = `
有使用者申請重新綁定 Email。

使用者帳號：${user.username}
原本 Email：${user.email}

請客服人員儘速手動處理此請求。
    `;
    await this.triggerEmail('irisyen115@gmail.com', '【重新綁定 Email 請求】', body);
    return { message: '申請已送出，客服將會協助您重新綁定 Email' };
  }
}
