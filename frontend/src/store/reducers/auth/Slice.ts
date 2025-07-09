import { createSlice, type PayloadAction } from '@reduxjs/toolkit';
import { anonym, type IAuthUser } from 'models/IAuthUser';

interface IAuthState {
  isFetching: boolean;
  error: string;
  isInitUser: boolean;
  user: IAuthUser;
  isBadConnection: boolean;
}

const initialState: IAuthState = {
  error: '',
  isBadConnection: false,
  isFetching: false,
  isInitUser: false,
  user: { ...anonym },
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
      state.user = anonym;
    },
    authFetchingSuccess(state, action: PayloadAction<IAuthUser>) {
      state.isFetching = false;
      state.error = '';
      state.user = action.payload;
    },
    initUserSuccess(state) {
      state.isInitUser = true;
    },
    isBadConnectionAuth(state) {
      state.isBadConnection = true;
    },
    isGoodConnectionAuth(state) {
      state.isBadConnection = false;
    },
  },
});

export default authSlice.reducer;
