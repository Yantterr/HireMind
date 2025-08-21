import { createSlice, type PayloadAction } from '@reduxjs/toolkit';
import { type User } from 'types/AuthTypes';

interface IAuthState {
  isFetching: boolean;
  error: string;
  isInitUser: boolean;
  user: User;
  isBadConnection: boolean;
  currentModalOverlay: string | null;
}

const anonym: User = { id: 0, isActivated: false, role: 'anonym' };

const initialState: IAuthState = {
  error: '',
  isBadConnection: false,
  isFetching: false,
  isInitUser: false,
  user: { ...anonym },
  currentModalOverlay: null,
};

export const authSlice = createSlice({
  initialState,
  name: 'auth',
  reducers: {
    authFetching(state) {
      state.isFetching = true;
    },
    authFetchingError(state, action: PayloadAction<string>) {
      state.isFetching = false;
      state.error = action.payload;
    },
    authFetchingSuccess(state) {
      state.isFetching = false;
      state.error = '';
    },
    authSetUser(state, action: PayloadAction<User>) {
      state.user = action.payload;
    },

    setCurrentModalOverlay(state, action: PayloadAction<string | null>) {
      if (action.payload === null || action.payload === state.currentModalOverlay) {
        state.currentModalOverlay = null;
      } else {
        state.currentModalOverlay = action.payload;
      }
    },

    initUserSuccess(state) {
      state.isInitUser = true;
    },
    // isBadConnectionAuth(state) {
    //   state.isBadConnection = true;
    // },
    // isGoodConnectionAuth(state) {
    //   state.isBadConnection = false;
    // },
  },
});

export default authSlice.reducer;
