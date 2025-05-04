import { IsNotEmpty } from 'class-validator';

export class VerifyCodeDto {
  @IsNotEmpty()
  username: string;

  @IsNotEmpty()
  verificationCode: string;
}
