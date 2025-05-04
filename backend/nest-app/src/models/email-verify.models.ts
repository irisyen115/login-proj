import { Entity, PrimaryGeneratedColumn, Column, CreateDateColumn, OneToOne, JoinColumn } from 'typeorm';
import { User } from './user.models';

@Entity('email_verification')
export class EmailVerify {
  @PrimaryGeneratedColumn()
  id: number;

  @CreateDateColumn({ name: 'created_at' })
  createdAt: Date;

  @Column({ name: 'valid_until', type: 'timestamp' })
  validUntil: Date;

  @Column({ name: 'email_verify_code', type: 'varchar', length: 50, nullable: true })
  emailVerifyCode: string;

  @Column({ name: 'user_id', unique: true })
  userId: number;

  @OneToOne(() => User, user => user.emailVerification, { onDelete: 'CASCADE' })
  @JoinColumn({ name: 'user_id' })
  user: User;
}
