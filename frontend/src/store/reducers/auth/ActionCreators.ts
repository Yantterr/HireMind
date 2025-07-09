import { authAPI } from 'api/api';
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
    const result = await authAPI.me();
    dispatch(
      authSlice.actions.authFetchingSuccess({
        id: result.data.id.toString(),
        name: result.data.username || '',
        role: result.data.role,
      }),
    );
  } catch (e) {
    console.log(e.response?.data?.detail);
    console.log(e.message);
    dispatch(authSlice.actions.authFetchingSuccess(anonym));
  }
  dispatch(authSlice.actions.initUserSuccess());
};

export const loginAuth =
  (login: string, password: string) => async (dispatch: AppDispatch, getStore: () => RootState) => {
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
      await authAPI.login(login, password);
      const result = await authAPI.me();
      dispatch(
        authSlice.actions.authFetchingSuccess({
          id: result.data.id.toString(),
          name: result.data.username,
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
  const refresh = localStorage.getItem('refresh');
  if (!refresh) {
    toast.info('Вы уже вышли из приложения.', {
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
    await authAPI.logout();
  } catch (error) {
    console.error(error);
  }
  dispatch(authSlice.actions.authFetchingSuccess(anonym));
  localStorage.removeItem('refresh');
  localStorage.removeItem('access');
};

export default null;
