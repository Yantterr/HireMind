import { Box, Button, TextField, Typography } from '@mui/material';
import { useAppDispatch } from 'hooks/redux';
import { useSnackbar } from 'notistack';
import type { ChangeEvent, FormEvent } from 'react';
import { useState } from 'react';
import { createUserAuth } from 'store/reducers/auth/ActionCreators';

interface RegisterFormData {
  login: string;
  email: string;
  password: string;
  confirmPassword: string;
}

const RegisterForm = () => {
  const dispatch = useAppDispatch();
  const { enqueueSnackbar } = useSnackbar();
  const [form, setForm] = useState<RegisterFormData>({
    confirmPassword: '',
    email: '',
    login: '',
    password: '',
  });

  const [error, setError] = useState<string | null>(null);

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value,
    });
    setError(null);
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (form.password !== form.confirmPassword) {
      setError('Пароли не совпадают');
      enqueueSnackbar('Пароли не совпадают', { variant: 'warning' });
      return;
    }
    dispatch(createUserAuth(form.login, form.email, form.password));
  };

  return (
    <Box
      component="form"
      onSubmit={handleSubmit}
      sx={{
        display: 'flex',
        flexDirection: 'column',
        gap: 2,
        maxWidth: 400,
        mt: 5,
        mx: 'auto',
      }}
    >
      <Typography variant="h5" component="h1" align="center">
        Регистрация
      </Typography>
      <TextField
        name="login"
        label="Логин"
        type="login"
        variant="outlined"
        value={form.login}
        onChange={handleChange}
        required
        fullWidth
      />
      <TextField
        name="email"
        label="E-mail"
        type="email"
        variant="outlined"
        value={form.email}
        onChange={handleChange}
        required
        fullWidth
      />
      <TextField
        name="password"
        label="Пароль"
        type="password"
        variant="outlined"
        value={form.password}
        onChange={handleChange}
        required
        fullWidth
      />
      <TextField
        name="confirmPassword"
        label="Подтвердите пароль"
        type="password"
        variant="outlined"
        value={form.confirmPassword}
        onChange={handleChange}
        required
        fullWidth
        error={Boolean(error)}
        helperText={error}
      />
      <Button type="submit" variant="contained" color="primary" fullWidth>
        Зарегистрироваться
      </Button>
    </Box>
  );
};

export default RegisterForm;
