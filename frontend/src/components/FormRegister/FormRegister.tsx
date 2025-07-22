import { Box, Button, TextField, Typography } from '@mui/material';
import { useAppDispatch } from 'hooks/redux';
import { useSnackbar } from 'notistack';
import type { ChangeEvent, FormEvent } from 'react';
import { useState } from 'react';
import { createUserAuth } from 'store/reducers/auth/ActionCreators';

const passwordConfig = Object.freeze({
  minLength: 12,
  oneDigit: true,
  oneLowercaseChar: true,
  oneSpecialChar: true,
  oneUppercaseChar: true,
});

function verifyPasswordStrength(password: string): string {
  if (passwordConfig.minLength && password.length < passwordConfig.minLength) {
    return `Ваш пароль должен содержать минимум ${passwordConfig.minLength} символов.`;
  }

  if (passwordConfig.oneLowercaseChar && password.search(/[a-z]/i) < 0) {
    return 'Ваш пароль должен содержать как минимум один строчный символ (a-z).';
  }

  if (passwordConfig.oneUppercaseChar && password.search(/[A-Z]/) < 0) {
    return 'Ваш пароль должен содержать как минимум одну заглавную букву (A–Z).';
  }

  if (passwordConfig.oneDigit && password.search(/\d/) < 0) {
    return 'Ваш пароль должен содержать как минимум одну цифру.';
  }

  if (passwordConfig.oneSpecialChar && password.search(/\W/) < 0) {
    return 'Ваш пароль должен содержать как минимум один специальный символ.';
  }

  return '';
}

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

  const [passwordError, setPasswordError] = useState<string | null>(null);
  const [confirmPasswordError, setConfirmPasswordError] = useState<string | null>(null);

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value,
    });
    if (e.target.name == 'password') {
      const result = verifyPasswordStrength(e.target.value);
      if (result) {
        setPasswordError(result);
        return;
      }
      setPasswordError(null);
    }
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (form.password !== form.confirmPassword) {
      setConfirmPasswordError('Пароли не совпадают');
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
        error={Boolean(passwordError)}
        helperText={passwordError}
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
        error={Boolean(confirmPasswordError)}
        helperText={confirmPasswordError}
      />
      <Button type="submit" variant="contained" color="primary" fullWidth>
        Зарегистрироваться
      </Button>
    </Box>
  );
};

export default RegisterForm;
