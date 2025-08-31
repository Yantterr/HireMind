import type { AppDispatch, RootState } from 'store/store';
import { chatsSlice } from './Slice';
import { chatsAPI } from 'api/api';
import type { ICreateChat } from 'types/ChatsTypes';

export const getChats = () => async (dispatch: AppDispatch) => {
  try {
    dispatch(chatsSlice.actions.chatsFetching());
    const chats = await chatsAPI.getAllChat();
    dispatch(chatsSlice.actions.setChats(chats.data));
    dispatch(chatsSlice.actions.chatsFetchingSuccess());
  } catch (e) {
    console.log(e.response?.data?.detail);
    console.log(e.message);
    dispatch(chatsSlice.actions.chatsFetchingError(e.message));
  }
};

export const createChat = (data: ICreateChat, next?: () => void) => async (dispatch: AppDispatch) => {
  try {
    dispatch(chatsSlice.actions.chatsFetching());
    const chat = await chatsAPI.createChat(data);
    dispatch(chatsSlice.actions.setChat(chat.data));
    const chats = await chatsAPI.getAllChat();
    dispatch(chatsSlice.actions.setChats(chats.data));
    dispatch(chatsSlice.actions.chatsFetchingSuccess());
    if (next) {
      next();
    }
  } catch (e) {
    console.log(e.response?.data?.detail);
    console.log(e.message);
    dispatch(chatsSlice.actions.chatsFetchingError(e.message));
  }
};

export const selectChat = (id: number) => async (dispatch: AppDispatch) => {
  try {
    dispatch(chatsSlice.actions.chatsFetching());
    const chat = await chatsAPI.getChat(id);
    dispatch(chatsSlice.actions.setChat(chat.data));
    dispatch(chatsSlice.actions.chatsFetchingSuccess());
  } catch (e) {
    console.log(e.response?.data?.detail);
    console.log(e.message);
    dispatch(chatsSlice.actions.chatsFetchingError(e.message));
  }
};

export const sendMessage = (content: string) => async (dispatch: AppDispatch, getStore: () => RootState) => {
  let checkInterval: NodeJS.Timeout | null = null;

  try {
    dispatch(chatsSlice.actions.chatsFetching());
    const state = getStore();

    if (!state.chatsReducer.selectedChat) {
      dispatch(chatsSlice.actions.chatsFetchingError("Chat doesn't exist"));
      return;
    }

    const response = await chatsAPI.sendMessage(state.chatsReducer.selectedChat.id, content);
    const chat = response.data;

    dispatch(chatsSlice.actions.setChat(chat));
    dispatch(chatsSlice.actions.chatsFetchingSuccess());

    if (chat.queue_position !== 0) {
      checkInterval = setInterval(async () => {
        try {
          const currentState = getStore();

          if (!currentState.chatsReducer.selectedChat || currentState.chatsReducer.selectedChat.id !== chat.id) {
            if (checkInterval) clearInterval(checkInterval);
            return;
          }

          const updatedChatResponse = await chatsAPI.getChat(chat.id);
          const updatedChat = updatedChatResponse.data;

          dispatch(chatsSlice.actions.setChat(updatedChat));

          if (updatedChat.queue_position === 0) {
            if (checkInterval) clearInterval(checkInterval);
          }
        } catch (error) {
          console.error('Failed to check queue status:', error);
        }
      }, 5000);
    }
  } catch (e) {
    console.log(e.response?.data?.detail);
    console.log(e.message);
    dispatch(chatsSlice.actions.chatsFetchingError(e.message));

    if (checkInterval) clearInterval(checkInterval);
  }
};
