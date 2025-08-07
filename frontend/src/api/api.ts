import type { AxiosResponse } from 'axios';
import type { NewChatRequest, NewMessageRequest } from 'models/request/Chat';
import type { UserResponse } from 'models/response/Auth';
import type { ChatResponse, PaginatedChatsResponse } from 'models/response/Chat';

import { instance } from './instances';

export const authAPI = {
  async createUser(email: string, username: string, password: string): Promise<AxiosResponse<UserResponse>> {
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
  async createChat(data: NewChatRequest): Promise<AxiosResponse<ChatResponse>> {
    return instance.post<ChatResponse>('/chats/', data);
  },

  async createNewMassage(chatId: number, data: NewMessageRequest): Promise<AxiosResponse<ChatResponse>> {
    return instance.put<ChatResponse>(`/chats/${chatId}/messages`, data);
  },

  async deleteChat(chatId: number): Promise<AxiosResponse<ChatResponse>> {
    return instance.delete<ChatResponse>(`/chats/${chatId}/`);
  },

  async getAllChat(page: number, perPage: number): Promise<AxiosResponse<PaginatedChatsResponse>> {
    return instance.get<PaginatedChatsResponse>('/chats/', {
      params: {
        page,
        per_page: perPage,
      },
    });
  },

  async getChat(chatId: number): Promise<AxiosResponse<ChatResponse>> {
    return instance.get<ChatResponse>(`/chats/${chatId}/`);
  },
};

export const usersAPI = {
  async confirmEmail(pinCode: string): Promise<AxiosResponse<UserResponse>> {
    return instance.patch<UserResponse>('/users/confirm_email', {
      key: pinCode,
    });
  },

  async me(): Promise<AxiosResponse<UserResponse>> {
    return instance.get<UserResponse>('/users/me');
  },

  async requestPinCode(): Promise<AxiosResponse<void>> {
    return instance.patch<void>('/users/key');
  },
};
