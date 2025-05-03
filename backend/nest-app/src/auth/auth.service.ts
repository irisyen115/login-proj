import { Injectable } from '@nestjs/common';
import { OAuth2Client } from 'google-auth-library';
import { ConfigService } from '@nestjs/config';
import { UsersService } from '../users/users.service';
import { RedisService } from '../common/utils/redis.util';

@Injectable()
export class AuthService {
  private googleClient: OAuth2Client;

  constructor(
    private usersService: UsersService,
    private redisService: RedisService,
    private configService: ConfigService,
  ) {
    this.googleClient = new OAuth2Client(this.configService.get('GOOGLE_CLIENT_ID'));
  }

  async authenticateGoogleUser(idToken: string) {
    try {
      const ticket = await this.googleClient.verifyIdToken({
        idToken,
        audience: this.configService.get('GOOGLE_CLIENT_ID'),
      });

      const payload = ticket.getPayload();
      const email = payload.email;
      const name = payload.name;
      const picture = payload.picture;

      if (!email) return { user: null, error: '無法取得使用者的 email' };

      let user = await this.usersService.findByEmail(email);
      if (!user) {
        user = await this.usersService.create({ email, username: name });
      }

      if (picture) {
        await this.usersService.updateProfileImage(user.id, picture);
      }

      await this.redisService.updateLoginCache(user.id);
      await this.usersService.updateLastLogin(user.id);

      return { user, error: null };
    } catch (err) {
      return { user: null, error: err.message };
    }
  }

  async register(data: any) {
    return this.usersService.register(data);
  }

  async login(data: any) {
    return this.usersService.login(data);
  }
}
