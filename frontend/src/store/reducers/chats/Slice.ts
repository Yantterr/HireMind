import { createSlice, type PayloadAction } from '@reduxjs/toolkit';
import type { IChat, TChats } from 'types/ChatsTypes';

interface IChatsState {
  isFetching: boolean;
  error: string;
  chats: TChats;
  selectedChat?: IChat;
}

const initialState: IChatsState = {
  error: '',
  isFetching: false,
  chats: [],
};

export const chatsSlice = createSlice({
  initialState,
  name: 'chats',
  reducers: {
    chatsFetching(state) {
      state.isFetching = true;
    },
    chatsFetchingError(state, action: PayloadAction<string>) {
      state.isFetching = false;
      state.error = action.payload;
    },
    chatsFetchingSuccess(state) {
      state.isFetching = false;
      state.error = '';
    },
    setChats(state, action: PayloadAction<TChats>) {
      state.chats = action.payload;
    },
    setChat(state, action: PayloadAction<IChat | undefined>) {
      state.selectedChat = action.payload;
    },
  },
});

export default chatsSlice.reducer;
