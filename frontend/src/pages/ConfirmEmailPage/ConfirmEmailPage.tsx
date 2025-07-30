import FormConfirmEmail from 'components/FormConfirmEmail/FormConfirmEmail';
import { useAppSelector } from 'hooks/redux';
import { useSnackbar } from 'notistack';
import { useEffect } from 'react';
import { Navigate, useLocation } from 'react-router-dom';

function ConfirmEmail() {
  const { isActivated } = useAppSelector((state) => state.authReducer.user);
  const location = useLocation();
  const { enqueueSnackbar } = useSnackbar();

  useEffect(() => {
    if (isActivated) {
      enqueueSnackbar('Почта уже подтверждена.', { variant: 'success' });
    }
  }, [enqueueSnackbar, isActivated]);

  if (isActivated) {
    return <Navigate to="/profile" state={{ from: location }} replace />;
  }

  return <FormConfirmEmail />;
}

export default ConfirmEmail;
