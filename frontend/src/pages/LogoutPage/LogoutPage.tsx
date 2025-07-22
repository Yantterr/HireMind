import { useAppDispatch } from 'hooks/redux';
import { useEffect } from 'react';
import { logoutAuth } from 'store/reducers/auth/ActionCreators';

export default function LogoutPage() {
  const dispatch = useAppDispatch();
  useEffect(() => {
    dispatch(logoutAuth());
  }, [dispatch]);
  return <div>Выходим из приложения ...</div>;
}
