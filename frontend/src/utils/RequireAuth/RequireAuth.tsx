import { Navigate, Outlet, useLocation } from 'react-router-dom';

import { useAppSelector } from '../../hooks/redux';

function RequireAuth() {
  const { role } = useAppSelector((state) => state.authReducer.user);
  const location = useLocation();

  return role === 'anonym' ? <Navigate to="/login" state={{ from: location }} replace /> : <Outlet />;
}

export default RequireAuth;
