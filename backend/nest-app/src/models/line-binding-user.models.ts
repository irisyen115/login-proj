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

@Table({ tableName: 'line_binding_user', timestamps: false })
export class LineBindingUser extends Model<
  {
    lineId: string;
    createdAt: Date;
    userId: number;
  },
  {
    lineId: string;
    userId: number;
  }
> {
  @PrimaryKey
  @Column({ type: DataTypes.STRING(120), field: 'line_id' })
  declare lineId: string;

  @CreatedAt
  @Column({ field: 'created_at' })
  declare createdAt: Date;

  @ForeignKey(() => User)
  @Column({ field: 'user_id' })
  declare userId: number;

  @BelongsTo(() => User, { foreignKey: 'userId', onDelete: 'CASCADE' })
  declare user: User;
}
