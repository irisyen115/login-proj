import {
    Entity,
    PrimaryGeneratedColumn,
    Column,
    CreateDateColumn,
    UpdateDateColumn,
    OneToMany,
    OneToOne,
  } from 'typeorm';
  import { PasswordVerify } from './password-verify.models';
  import { EmailVerify } from './email-verify.models';
  import { LineBindingUser } from './line-binding-user.models';
  import * as bcrypt from 'bcrypt';

  @Entity('users')
  export class User {
    @PrimaryGeneratedColumn()
    id: number;

    @Column({ length: 50 })
    username: string;

    @Column({ type: 'text', nullable: true })
    passwordHash: string;

    @Column({
      type: 'enum',
      enum: ['user', 'admin', 'guest'],
      default: 'user',
    })
    role: 'user' | 'admin' | 'guest';

    @CreateDateColumn({ name: 'created_at' })
    createdAt: Date;

    @UpdateDateColumn({ name: 'updated_at' })
    updatedAt: Date;

    @Column({ name: 'last_login', type: 'timestamp', nullable: true })
    lastLogin: Date;

    @Column({ name: 'login_count', default: 0 })
    loginCount: number;

    @Column({ name: 'profile_image', length: 255, nullable: true })
    profileImage: string;

    @Column({ name: 'picture_name', length: 255, nullable: true })
    pictureName: string;

    @Column({ length: 254, nullable: true })
    email: string;

    // Relations
    @OneToMany(() => PasswordVerify, pv => pv.user, { cascade: true })
    passwordVerification: PasswordVerify[];

    @OneToOne(() => EmailVerify, ev => ev.user, { cascade: true })
    emailVerification: EmailVerify;

    @OneToMany(() => LineBindingUser, lb => lb.user, { cascade: true })
    lineBindingUser: LineBindingUser[];

    // Methods

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
  }
