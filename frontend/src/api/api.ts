import type { AxiosResponse } from 'axios';

import { instance } from './instances';
import type { SystemRole } from 'types/AuthTypes';
import type { IChat, TChats, ICreateChat } from 'types/ChatsTypes';

type UserResponse = {
  id: number;
  email: string;
  username: string;
  role: SystemRole;
  is_activated: boolean;
};

export const authAPI = {
  async register(email: string, username: string, password: string): Promise<AxiosResponse<UserResponse>> {
    return instance.post<UserResponse>('/auth/register', {
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
};

export const chatsAPI = {
  async createChat(data: ICreateChat): Promise<AxiosResponse<IChat>> {
    return instance.post<IChat>('/chats/', data);
  },
  async sendMessage(chatId: number, data: string): Promise<AxiosResponse<IChat>> {
    return instance.post<IChat>(`/chats/${chatId}/messages`, {
      content: data,
      role: 'user',
    });
  },
  //   async createNewMassage(chatId: number, data: NewMessageRequest): Promise<AxiosResponse<ChatResponse>> {
  //     return instance.put<ChatResponse>(`/chats/${chatId}/messages`, data);
  //   },

  //   async deleteChat(chatId: number): Promise<AxiosResponse<ChatResponse>> {
  //     return instance.delete<ChatResponse>(`/chats/${chatId}/`);
  //   },
  async getAllChat(): Promise<AxiosResponse<TChats>> {
    return instance.get<TChats>('/chats/');
  },
  async getChat(chatId: number): Promise<AxiosResponse<IChat>> {
    return instance.get<IChat>(`/chats/${chatId}`);
  },
};

export const usersAPI = {
  async confirmEmail(pinCode: number): Promise<AxiosResponse<UserResponse>> {
    return instance.patch<UserResponse>('/users/confirm-email', {
      key: pinCode,
    });
  },

  async me(): Promise<AxiosResponse<UserResponse>> {
    return instance.get<UserResponse>('/users/me');
  },

  async getNewKey(): Promise<AxiosResponse<void>> {
    return instance.post<void>('/users/key');
  },
};
