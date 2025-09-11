/**
 * Authentication constants
 */
import type { User } from '../types/auth';

export const DEV_USER: User = {
  id: '1',
  email: 'john.doe@example.com',
  username: 'johndoe',
  name: 'John Doe',
  roles: ['user', 'admin'],
  isDevMode: true,
} as const;
