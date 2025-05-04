import {
    Entity,
    Column,
    PrimaryColumn,
    CreateDateColumn,
    ManyToOne,
    JoinColumn,
  } from 'typeorm';
  import { User } from './user.models';

  @Entity('line_binding_user')
  export class LineBindingUser {
    @PrimaryColumn({ name: 'line_id', type: 'varchar', length: 120 })
    lineId: string;

    @CreateDateColumn({ name: 'created_at' })
    createdAt: Date;

    @Column({ name: 'user_id' })
    userId: number;

    @ManyToOne(() => User, user => user.lineBindingUser, { onDelete: 'CASCADE' })
    @JoinColumn({ name: 'user_id' })
    user: User;
  }
