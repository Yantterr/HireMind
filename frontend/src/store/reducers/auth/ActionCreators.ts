import { authAPI, usersAPI } from 'api/api';
import { anonym } from 'models/IAuthUser';
import { toast } from 'react-toastify';
import type { AppDispatch, RootState } from 'store/store';

import { authSlice } from './Slice';

export const getCurrentUser = () => async (dispatch: AppDispatch, getStore: () => RootState) => {
  const { isFetching } = getStore().authReducer;
  if (isFetching) {
    return;
  }
  try {
    dispatch(authSlice.actions.authFetching());
    const result = await usersAPI.me();
    dispatch(
      authSlice.actions.authFetchingUserSuccess({
        email: result.data.email,
        id: result.data.id.toString(),
        isActivated: result.data.is_activated,
        login: result.data.username,
        role: result.data.role,
      }),
    );
  } catch (e) {
    console.log(e.response?.data?.detail);
    console.log(e.message);
    dispatch(authSlice.actions.authFetchingUserSuccess(anonym));
  }
  dispatch(authSlice.actions.initUserSuccess());
};

export const loginAuth =
  (email: string, password: string) => async (dispatch: AppDispatch, getStore: () => RootState) => {
    const { isFetching } = getStore().authReducer;
    if (isFetching) {
      toast.info('Ожидайте, ждем ответа от сервера ...', {
        autoClose: 5000,
        closeOnClick: true,
        draggable: true,
        hideProgressBar: false,
        pauseOnHover: true,
        position: 'top-right',
        theme: 'colored',
      });
      return;
    }
    try {
      dispatch(authSlice.actions.authFetching());
      const result = await authAPI.login(email, password);
      dispatch(
        authSlice.actions.authFetchingUserSuccess({
          email: result.data.email,
          id: result.data.id.toString(),
          isActivated: result.data.is_activated,
          login: result.data.username,
          role: result.data.role,
        }),
      );
    } catch (e) {
      console.log(e.response?.data?.detail);
      console.log(e.message);
      toast.warn('Не правильный логин или пароль', {
        autoClose: 5000,
        closeOnClick: true,
        draggable: true,
        hideProgressBar: false,
        pauseOnHover: true,
        position: 'top-right',
        theme: 'colored',
      });
      dispatch(authSlice.actions.authFetchingError(e.message));
    }
  };

export const logoutAuth = () => async (dispatch: AppDispatch, getStore: () => RootState) => {
  const { isFetching } = getStore().authReducer;
  if (isFetching) {
    toast.info('Ожидайте, ждем ответа от сервера ...', {
      autoClose: 5000,
      closeOnClick: true,
      draggable: true,
      hideProgressBar: false,
      pauseOnHover: true,
      position: 'top-right',
      theme: 'colored',
    });
    return;
  }
  try {
    dispatch(authSlice.actions.authFetching());
    const result = await authAPI.logout();
    console.log(result);
    dispatch(authSlice.actions.authFetchingUserSuccess(anonym));
  } catch (e) {
    console.error(e);
    dispatch(authSlice.actions.authFetchingError(e.message));
  }
};

export const createUserAuth =
  (login: string, email: string, password: string) => async (dispatch: AppDispatch, getStore: () => RootState) => {
    const { isFetching } = getStore().authReducer;
    if (isFetching) {
      toast.info('Ожидайте, ждем ответа от сервера ...', {
        autoClose: 5000,
        closeOnClick: true,
        draggable: true,
        hideProgressBar: false,
        pauseOnHover: true,
        position: 'top-right',
        theme: 'colored',
      });
      return;
    }
    try {
      dispatch(authSlice.actions.authFetching());
      const result = await authAPI.createUser(email, login, password);
      dispatch(
        authSlice.actions.authFetchingUserSuccess({
          email: result.data.email,
          id: result.data.id.toString(),
          isActivated: result.data.is_activated,
          login: result.data.username,
          role: result.data.role,
        }),
      );
    } catch (e) {
      console.log(e.response?.data?.detail);
      console.log(e.message);
      toast.warn('Регистрация завершилась с ошибкой', {
        autoClose: 5000,
        closeOnClick: true,
        draggable: true,
        hideProgressBar: false,
        pauseOnHover: true,
        position: 'top-right',
        theme: 'colored',
      });
      dispatch(authSlice.actions.authFetchingError(e.message));
    }
  };

export const confirmEmail = (pinCode: string) => async (dispatch: AppDispatch, getStore: () => RootState) => {
  const { isFetching } = getStore().authReducer;
  if (isFetching) {
    toast.info('Ожидайте, ждем ответа от сервера ...', {
      autoClose: 5000,
      closeOnClick: true,
      draggable: true,
      hideProgressBar: false,
      pauseOnHover: true,
      position: 'top-right',
      theme: 'colored',
    });
    return;
  }
  try {
    dispatch(authSlice.actions.authFetching());
    const result = await usersAPI.confirmEmail(pinCode);
    dispatch(
      authSlice.actions.authFetchingUserSuccess({
        email: result.data.email,
        id: result.data.id.toString(),
        isActivated: result.data.is_activated,
        login: result.data.username,
        role: result.data.role,
      }),
    );
  } catch (e) {
    console.log(e.response?.data?.detail);
    console.log(e.message);
    dispatch(authSlice.actions.authFetchingError(e.message));
  }
};

export const requestPinCode = () => async (dispatch: AppDispatch, getStore: () => RootState) => {
  const { isFetching } = getStore().authReducer;
  if (isFetching) {
    toast.info('Ожидайте, ждем ответа от сервера ...', {
      autoClose: 5000,
      closeOnClick: true,
      draggable: true,
      hideProgressBar: false,
      pauseOnHover: true,
      position: 'top-right',
      theme: 'colored',
    });
    return;
  }
  try {
    dispatch(authSlice.actions.authFetching());
    await usersAPI.requestPinCode();
    dispatch(authSlice.actions.authFetchingSuccess());
  } catch (e) {
    console.log(e.response?.data?.detail);
    console.log(e.message);
    dispatch(authSlice.actions.authFetchingError(e.message));
  }
};

export default null;
