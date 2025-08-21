import { authAPI, usersAPI } from 'api/api';
import type { AppDispatch } from 'store/store';

import { authSlice } from './Slice';

export const editCurrentModalOverlay = (action: string | null) => (dispatch: AppDispatch) => {
  dispatch(authSlice.actions.authFetchingSuccess());
  dispatch(authSlice.actions.setCurrentModalOverlay(action));
};

export const getCurrentUser = () => async (dispatch: AppDispatch) => {
  try {
    dispatch(authSlice.actions.authFetching());
    const result = await usersAPI.me();
    dispatch(
      authSlice.actions.authSetUser({
        email: result.data.email,
        id: result.data.id,
        isActivated: result.data.is_activated,
        username: result.data.username,
        role: result.data.role,
      }),
    );
    dispatch(authSlice.actions.authFetchingSuccess());
  } catch (e) {
    console.log(e.response?.data?.detail);
    console.log(e.message);
    dispatch(authSlice.actions.authFetchingError(e.message));
  }
  dispatch(authSlice.actions.initUserSuccess());
};

export const loginAuth = (email: string, password: string) => async (dispatch: AppDispatch) => {
  try {
    dispatch(authSlice.actions.authFetching());
    const result = await authAPI.login(email, password);
    dispatch(
      authSlice.actions.authSetUser({
        email: result.data.email,
        id: result.data.id,
        isActivated: result.data.is_activated,
        username: result.data.username,
        role: result.data.role,
      }),
    );
    dispatch(authSlice.actions.authFetchingSuccess());
  } catch (e) {
    console.log(e.response?.data?.detail);
    console.log(e.message);
    dispatch(authSlice.actions.authFetchingError(e.response?.data?.detail));
  }
};

export const registerAuth =
  (email: string, password: string, username: string, next?: () => void) => async (dispatch: AppDispatch) => {
    try {
      dispatch(authSlice.actions.authFetching());
      const result = await authAPI.register(email, username, password);
      dispatch(
        authSlice.actions.authSetUser({
          email: result.data.email,
          id: result.data.id,
          isActivated: result.data.is_activated,
          username: result.data.username,
          role: result.data.role,
        }),
      );
      dispatch(authSlice.actions.authFetchingSuccess());
      if (next) {
        next();
      }
    } catch (e) {
      console.log(e.response?.data?.detail);
      console.log(e.message);
      dispatch(authSlice.actions.authFetchingError(e.response?.data?.detail));
    }
  };

export const logoutAuth = () => async (dispatch: AppDispatch) => {
  try {
    dispatch(authSlice.actions.authFetching());
    await authAPI.logout();
    const user = await usersAPI.me();
    dispatch(
      authSlice.actions.authSetUser({
        email: user.data.email,
        id: user.data.id,
        isActivated: user.data.is_activated,
        username: user.data.username,
        role: user.data.role,
      }),
    );
    dispatch(authSlice.actions.authFetchingSuccess());
  } catch (e) {
    console.log(e.response?.data?.detail);
    console.log(e.message);
    dispatch(authSlice.actions.authFetchingError(e.response?.data?.detail));
  }
};

export const confirmEmail = (pinCode: number) => async (dispatch: AppDispatch) => {
  try {
    dispatch(authSlice.actions.authFetching());
    const result = await usersAPI.confirmEmail(pinCode);
    dispatch(
      authSlice.actions.authSetUser({
        email: result.data.email,
        id: result.data.id,
        isActivated: result.data.is_activated,
        username: result.data.username,
        role: result.data.role,
      }),
    );
    dispatch(authSlice.actions.authFetchingSuccess());
  } catch (e) {
    console.log(e.response?.data?.detail);
    console.log(e.message);
    dispatch(authSlice.actions.authFetchingError(e.response?.data?.detail));
  }
};

export const getNewKey = () => async (dispatch: AppDispatch) => {
  try {
    dispatch(authSlice.actions.authFetching());
    await usersAPI.getNewKey();
    dispatch(authSlice.actions.authFetchingSuccess());
  } catch (e) {
    console.log(e.response?.data?.detail);
    console.log(e.message);
    dispatch(authSlice.actions.authFetchingError(e));
  }
};
