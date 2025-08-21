export type SystemRole = 'admin' | 'user' | 'anonym';

export interface User {
  id: number;
  email?: string;
  username?: string;
  role: SystemRole;
  isActivated: boolean;
}
