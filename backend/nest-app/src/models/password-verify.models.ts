import {
  Column,
  Model,
  Table,
  PrimaryKey,
  AutoIncrement,
  CreatedAt,
  ForeignKey,
  BelongsTo
} from 'sequelize-typescript';
import { User } from './user.models';
import { DataTypes } from 'sequelize';

@Table({ tableName: 'password_verification', timestamps: false })
export class PasswordVerify extends Model<PasswordVerify> {
  @PrimaryKey
  @AutoIncrement
  @Column
  declare id: number;

  @CreatedAt
  @Column({ field: 'created_at', defaultValue: DataTypes.NOW})
  declare createdAt: Date;

  @Column({ type: DataTypes.DATE, field: 'valid_until' })
  declare validUntil: Date;

  @Column({ type: DataTypes.STRING(50), field: 'password_verify_code', allowNull: true })
  declare passwordVerifyCode: string;

  @ForeignKey(() => User)
  @Column({ field: 'user_id' })
  declare userId: number;

  @BelongsTo(() => User, { foreignKey: 'userId', onDelete: 'CASCADE' })
  declare user: User;
}
