import { Injectable } from '@nestjs/common';
import { InjectModel } from '@nestjs/sequelize';
import { PasswordVerify } from '../models/password-verify.models';
import { User } from '../models/user.models';
import dayjs from 'dayjs';

@Injectable()
export class ResetService {
  constructor(
    @InjectModel(PasswordVerify)
    private passwordVerifyRepo: typeof PasswordVerify,
  ) {}

  async resetUserPassword(code: string, newPassword: string): Promise<{ message?: string; error?: string }> {
    try {
      const passwordVerify = await this.passwordVerifyRepo.findOne({
        where: { passwordVerifyCode: code },
        include: [{ model: User, as: 'user' }],
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
      await user.save();

      return { message: '密碼重設成功，請重新登入' };
    } catch (e) {
      return { error: `發生錯誤: ${e.message}` };
    }
  }
}
