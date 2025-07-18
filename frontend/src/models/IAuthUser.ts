import type { Role } from 'models/response/Auth';

export interface User {
  id: string;
  login: string;
  email: string;
  role: Role;
  isActivated: boolean;
}

export const anonym: User = {
  email: 'anonym',
  id: 'anonym',
  isActivated: true,
  login: 'anonym',
  role: 'anonym',
};
