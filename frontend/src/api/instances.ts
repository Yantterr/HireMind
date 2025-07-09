import * as axios from 'axios';
import { anonym } from 'models/IAuthUser';
import { authSlice } from 'store/reducers/auth/Slice';

import store from '../store/store';
import baseURL from './config';

export const instance = axios.default.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
    accept: 'application/json',
  },
});

instance.interceptors.response.use(
  (response) => {
    store.dispatch(authSlice.actions.isGoodConnectionAuth());
    return response;
  },
  async (error) => {
    if (error?.response?.status === undefined || error?.response?.status === 0) {
      store.dispatch(authSlice.actions.isBadConnectionAuth());
    } else if (error.response && error.response.status === 401) {
      store.dispatch(authSlice.actions.authFetchingSuccess(anonym));
    }

    throw error;
  },
);
