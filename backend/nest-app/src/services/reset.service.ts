import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { PasswordVerify } from '../models/password-verify.models';
import * as dayjs from 'dayjs';

@Injectable()
export class ResetService {
  constructor(
    @InjectRepository(PasswordVerify)
    private passwordVerifyRepo: Repository<PasswordVerify>,
  ) {}

  async resetUserPassword(code: string, newPassword: string): Promise<{ message?: string; error?: string }> {
    try {
      const passwordVerify = await this.passwordVerifyRepo.findOne({
        where: { passwordVerifyCode: code },
        relations: ['user'],
      });

      if (!passwordVerify) {
        return { error: '驗證密鑰不存在' };
      }

      if (dayjs().isAfter(dayjs(passwordVerify.validUntil))) {
        return { error: '驗證密鑰已過期' };
      }

      const user = passwordVerify.user;
      if (!user) {
        return { error: '找不到對應使用者' };
      }

      user.setPassword(newPassword);
      await this.passwordVerifyRepo.manager.save(user);

      return { message: '密碼重設成功，請重新登入' };
    } catch (e) {
      return { error: `發生錯誤: ${e.message}` };
    }
  }
}
