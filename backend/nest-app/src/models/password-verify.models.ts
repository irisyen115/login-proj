import {
    Entity,
    PrimaryGeneratedColumn,
    Column,
    CreateDateColumn,
    ManyToOne,
    JoinColumn,
  } from 'typeorm';
  import { User } from './user.models';

  @Entity('password_verification')
  export class PasswordVerify {
    @PrimaryGeneratedColumn()
    id: number;

    @CreateDateColumn({ name: 'created_at' })
    createdAt: Date;

    @Column({ name: 'valid_until', type: 'timestamp' })
    validUntil: Date;

    @Column({ name: 'password_verify_code', length: 50, nullable: true })
    passwordVerifyCode: string;

    @Column({ name: 'user_id' })
    userId: number;

    @ManyToOne(() => User, user => user.passwordVerification, { onDelete: 'CASCADE' })
    @JoinColumn({ name: 'user_id' })
    user: User;
  }
