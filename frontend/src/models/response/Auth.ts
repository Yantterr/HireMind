export type Role = 'admin' | 'user' | 'anonym';

export interface UserResponse {
  username: string;
  id: number;
  role: Role;
  is_activated: boolean;
  email: string;
}
