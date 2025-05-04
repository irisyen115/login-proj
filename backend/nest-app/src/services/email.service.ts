import { Injectable, NotFoundException, BadRequestException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { User } from '../models/user.models';
import { EmailVerify } from '../models/email-verify.models';
import { PasswordVerify } from '../models/password-verify.models';
import { Repository } from 'typeorm';
import * as crypto from 'crypto';
import { ConfigService } from '@nestjs/config';
import axios from 'axios';

@Injectable()
export class EmailService {
  constructor(
    @InjectRepository(User)
    private userRepo: Repository<User>,
    @InjectRepository(EmailVerify)
    private emailVerifyRepo: Repository<EmailVerify>,
    @InjectRepository(PasswordVerify)
    private passwordVerifyRepo: Repository<PasswordVerify>,
    private configService: ConfigService,
  ) {}

  private generateCode(length: number): string {
    return crypto.randomBytes(length).toString('hex').slice(0, length);
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
      throw new BadRequestException('Email 發送失敗');
    }
  }

  async sendAuthenticationEmail(username: string) {
    const user = await this.userRepo.findOne({ where: { username } });
    if (!user) throw new NotFoundException('用戶不存在');
    if (!user.email) throw new BadRequestException('用戶未綁定 Email');

    const existing = await this.passwordVerifyRepo.findOne({
      where: { user: { id: user.id } },
      order: { validUntil: 'DESC' },
    });

    if (existing && new Date() <= existing.validUntil) {
      return { message: '驗證碼已發送，請勿重複點取' };
    }

    const code = this.generateCode(30);
    const passwordVerify = this.passwordVerifyRepo.create({
      passwordVerifyCode: code,
      validUntil: new Date(Date.now() + 15 * 60 * 1000),
      user,
    });
    await this.passwordVerifyRepo.save(passwordVerify);

    const link = `${this.configService.get('IRIS_DS_SERVER_URL')}/reset-password/${code}`;
    await this.triggerEmail(user.email, '帳戶綁定確認', link);
    return { message: '驗證信已發送，請重新設置' };
  }

  async sendEmailVerification(username: string) {
    const user = await this.userRepo.findOne({ where: { username } });
    if (!user) throw new NotFoundException('用戶不存在');
    if (!user.email) throw new BadRequestException('未綁定 Email');

    const existing = await this.emailVerifyRepo.findOne({
      where: { user: { id: user.id } },
      order: { validUntil: 'DESC' },
    });

    if (existing && new Date() <= existing.validUntil) {
      return { message: '驗證碼已發送，請勿重複點取' };
    }

    const code = this.generateCode(6);
    const emailVerify = this.emailVerifyRepo.create({
      emailVerifyCode: code,
      validUntil: new Date(Date.now() + 15 * 60 * 1000),
      user,
    });
    await this.emailVerifyRepo.save(emailVerify);

    await this.triggerEmail(user.email, '帳戶綁定確認', code);
    return { message: '驗證碼已發送，請檢查電子郵件' };
  }

  async sendEmailCode(username: string, code: string) {
    const user = await this.userRepo.findOne({ where: { username } });
    if (!user) throw new NotFoundException('用戶不存在');

    const record = await this.emailVerifyRepo.findOne({
      where: { user: { id: user.id } },
      order: { validUntil: 'DESC' },
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
