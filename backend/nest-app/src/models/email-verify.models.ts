import {
  Column,
  Model,
  Table,
  PrimaryKey,
  CreatedAt,
  ForeignKey,
  BelongsTo
} from 'sequelize-typescript';
import { User } from './user.models';
import { DataTypes } from 'sequelize';

@Table({ tableName: 'email_verification', timestamps: false })
export class EmailVerify extends Model {
  @PrimaryKey
  @Column({ autoIncrement: true })
  declare id: number;

  @CreatedAt
  @Column({ type: DataTypes.DATE, field: 'created_at', defaultValue: DataTypes.NOW })
  declare createdAt: Date;

  @Column({ type: DataTypes.DATE, field: 'valid_until' })
  declare validUntil: Date;

  @Column({ type: DataTypes.STRING(50), field: 'email_verify_code', allowNull: true })
  declare emailVerifyCode: string;

  @ForeignKey(() => User)
  @Column({ field: 'user_id', unique: true })
  declare userId: number;

  @BelongsTo(() => User, { foreignKey: 'userId', onDelete: 'CASCADE' })
  declare user: User;
}
