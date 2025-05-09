import {
  Column,
  Model,
  Table,
  PrimaryKey,
  AutoIncrement,
  CreatedAt,
  UpdatedAt,
  Default,
  AllowNull,
  HasMany,
  HasOne
} from 'sequelize-typescript';
import { IsEnum } from 'class-validator';
import { PasswordVerify } from './password-verify.models';
import { EmailVerify } from './email-verify.models';
import { LineBindingUser } from './line-binding-user.models';
import * as bcrypt from 'bcryptjs';
import { DataTypes } from 'sequelize';
import { CreationAttributes } from 'sequelize';

@Table({ tableName: 'users' })
export class User extends Model<User> {
  @PrimaryKey
  @AutoIncrement
  @Column
  declare id: number;

  @Column({ allowNull: false, type: DataTypes.STRING(50) })
  declare username: string;

  @AllowNull(true)
  @Column({ type: DataTypes.TEXT, field: 'password_hash' })
  declare passwordHash: string;

  @Default('user')
  @IsEnum(['user', 'admin', 'guest'])
  @Column({
    type: DataTypes.ENUM,
    values: ['user', 'admin', 'guest'],
  })
  declare role: 'user' | 'admin' | 'guest';

  @CreatedAt
  @Column({ field: 'created_at' })
  declare createdAt: Date;

  @UpdatedAt
  @Column({ field: 'updated_at' })
  declare updatedAt: Date;

  @AllowNull(true)
  @Column({ type: DataTypes.DATE, field: 'last_login' })
  declare lastLogin: Date;

  @Default(0)
  @Column({ field: 'login_count', type: DataTypes.INTEGER, defaultValue: 0 })
  declare loginCount: number;


  @AllowNull(true)
  @Column({ field: 'profile_image', type: DataTypes.STRING(255) })
  declare profileImage: string;

  @AllowNull(true)
  @Column({ field: 'picture_name', type: DataTypes.STRING(255) })
  declare pictureName: string;

  @AllowNull(true)
  @Column({ type: DataTypes.STRING(254) })
  declare email: string;

  @HasMany(() => PasswordVerify, { foreignKey: 'userId', sourceKey: 'id', onDelete: 'CASCADE' })
  declare passwordVerification: PasswordVerify[];

  @HasOne(() => EmailVerify, { foreignKey: 'userId', sourceKey: 'id', onDelete: 'CASCADE' })
  declare emailVerification: EmailVerify;

  @HasMany(() => LineBindingUser, { foreignKey: 'userId', sourceKey: 'id', onDelete: 'CASCADE' })
  declare lineBindingUser: LineBindingUser[];

  async setPassword(password: string) {
    this.passwordHash = await bcrypt.hash(password, 10);
  }

  async checkPassword(password: string): Promise<boolean> {
    return bcrypt.compare(password, this.passwordHash);
  }

  updateLastLogin() {
    this.lastLogin = new Date();
    this.loginCount = (this.loginCount || 0) + 1;
  }

  toJSON() {
    const { passwordHash, ...rest } = this;
    return rest;
  }

  static fromJson(jsonData: any): User {
    const rawData = jsonData.dataValues ?? jsonData;
    if (rawData.loginCount) {
      rawData.loginCount = Number(rawData.loginCount);
    }
    if (rawData.lastLogin) {
      rawData.lastLogin = new Date(rawData.lastLogin);
    }

    if (rawData.createdAt) {
      rawData.createdAt = new Date(rawData.createdAt);
    }
    if (rawData.updatedAt) {
      rawData.updatedAt = new Date(rawData.updatedAt);
    }
    return User.build(rawData, { isNewRecord: false });
  }

  }

