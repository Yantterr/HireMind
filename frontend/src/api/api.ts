import type { AxiosResponse } from 'axios';
import type { IAuthResponse } from 'models/response/AuthResponse';

import { instance } from './instances';

export const authAPI = {
  async login(username: string, password: string): Promise<void> {
    return instance.post('/users/login/', {
      password,
      username,
    });
  },

  async logout(): Promise<void> {
    return instance.post('/users/logout/');
  },

  async me(): Promise<AxiosResponse<IAuthResponse>> {
    return instance.get<IAuthResponse>('/users/me?hash=1');
  },
};
