import type { AxiosResponse } from 'axios';
import type { NewChatRequest } from 'models/request/Chat';
import type { UserResponse } from 'models/response/Auth';
import type { ChatResponse, ShortChatResponse } from 'models/response/Chat';

import { instance } from './instances';

export const authAPI = {
  async confirmEmail(pinCode: string): Promise<AxiosResponse<UserResponse>> {
    return instance.patch<UserResponse>('/auth/confirm_email', {
      key: pinCode,
    });
  },

  async createUser(email: string, username: string, password: string): Promise<AxiosResponse<UserResponse>> {
    return instance.post<UserResponse>('/auth/', {
      email,
      password,
      username,
    });
  },

  async login(email: string, password: string): Promise<AxiosResponse<UserResponse>> {
    return instance.post<UserResponse>('/auth/login', {
      email,
      password,
    });
  },

  async logout(): Promise<void> {
    return instance.post('/auth/logout/');
  },

  async me(): Promise<AxiosResponse<UserResponse>> {
    return instance.get<UserResponse>('/auth/me');
  },

  async requestPinCode(): Promise<AxiosResponse<void>> {
    return instance.get<void>('/auth/key');
  },
};

export const gptAPI = {
  async createChat(data: NewChatRequest): Promise<AxiosResponse<ChatResponse>> {
    return instance.post<ChatResponse>('/gpt/', data);
  },

  async deleteChat(chatId: number): Promise<AxiosResponse<ChatResponse>> {
    return instance.delete<ChatResponse>(`/gpt/${chatId}/`);
  },

  async getAllChat(): Promise<AxiosResponse<ShortChatResponse[]>> {
    return instance.get<ShortChatResponse[]>('/gpt/');
  },

  async getChat(chatId: number): Promise<AxiosResponse<ChatResponse>> {
    return instance.get<ChatResponse>(`/gpt/${chatId}/`);
  },
};
