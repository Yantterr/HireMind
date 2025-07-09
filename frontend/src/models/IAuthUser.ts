import type { Role } from 'models/response/AuthResponse';

export interface IAuthUser {
  id: string;
  name: string;
  role: Role;
}

export const anonym: IAuthUser = {
  id: 'anonym',
  name: 'anonym',
  role: 'anonym',
};
