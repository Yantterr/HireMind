import FormConfirmEmail from 'components/FormConfirmEmail/FormConfirmEmail';
import { useAppSelector } from 'hooks/redux';
import { Navigate, useLocation } from 'react-router-dom';

function ConfirmEmail() {
  const { isActivated } = useAppSelector((state) => state.authReducer.user);
  const location = useLocation();

  if (isActivated) return <Navigate to="/profile" state={{ from: location }} replace />;

  return <FormConfirmEmail />;
}

export default ConfirmEmail;
