import { Navigate, Outlet } from 'react-router-dom';

import { useAppSelector } from '../../hooks/redux';

function RequireAnonym() {
  const { role } = useAppSelector((state) => state.authReducer.user);

  return role !== 'anonym' ? <Navigate to="/home" replace /> : <Outlet />;
}

export default RequireAnonym;
