import LockOutlinedIcon from '@mui/icons-material/LockOutlined';
import { Avatar, Box, Button, Grid, Link, Typography } from '@mui/material';
import ValidatedTextField from 'components/ValidatedTextField/ValidatedTextField';
import { useAppDispatch, useAppSelector } from 'hooks/redux';
import { useRef } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import { loginAuth } from 'store/reducers/auth/ActionCreators';

const FormLogin = () => {
  const dispatch = useAppDispatch();
  const { isFetching } = useAppSelector((state) => state.authReducer);
  console.log({ dispatch, isFetching, loginAuth });

  const formValid = useRef({ password: { isValid: false, value: '' }, username: { isValid: false, value: '' } });
  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (
      Object.values(formValid.current).every(({ isValid }) => {
        return isValid;
      })
    ) {
      dispatch(loginAuth(formValid.current.username.value, formValid.current.password.value));
    } else {
      alert('Form is invalid! Please check the fields...');
    }
  };

  return (
    <Box sx={{ ml: 1, mr: 1, mt: 2 }}>
      <Avatar
        sx={{
          bgcolor: 'secondary.main',
          mb: 1,
          mx: 'auto',
          textAlign: 'center',
        }}
      >
        <LockOutlinedIcon />
      </Avatar>
      <Typography component="h1" variant="h5" sx={{ textAlign: 'center' }}>
        Вход
      </Typography>
      <Box component="form" onSubmit={handleSubmit} noValidate sx={{ mt: 1 }}>
        <ValidatedTextField
          label="Username"
          placeholder="Enter username"
          required
          autoFocus
          validator={(value: string) => {
            console.log(value);
            return true;
          }}
          onChange={(value, isValid) => {
            formValid.current.username = { isValid, value };
          }}
          sx={{ mb: 2 }}
          disabled={isFetching}
        />
        <ValidatedTextField
          label="Password"
          placeholder="Enter password"
          required
          type="password"
          validator={(value: string) => {
            console.log(value);
            return true;
          }}
          onChange={(value, isValid) => (formValid.current.password = { isValid, value })}
          disabled={isFetching}
        />
        <Button type="submit" variant="contained" fullWidth sx={{ mt: 1 }} disabled={isFetching}>
          {isFetching ? 'Loading...' : 'Sign In'}
        </Button>
      </Box>
      <Grid container justifyContent="space-between" sx={{ mt: 1 }}>
        <Grid>
          <Link component={RouterLink} to="/forgot">
            Forgot password?
          </Link>
        </Grid>
        <Grid>
          <Link component={RouterLink} to="/register">
            Sign Up
          </Link>
        </Grid>
      </Grid>
    </Box>
  );
};

export default FormLogin;
