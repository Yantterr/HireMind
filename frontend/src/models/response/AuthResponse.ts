export type Role = 'admin' | 'user' | 'anonym';

export interface IAuthResponse {
  username: string;
  id: number;
  role: Role;
}
