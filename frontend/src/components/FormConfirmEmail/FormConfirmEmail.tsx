import { Box, Button, TextField } from '@mui/material';
import { useAppDispatch } from 'hooks/redux';
import { useSnackbar } from 'notistack';
import { useState } from 'react';
import { confirmEmail } from 'store/reducers/auth/ActionCreators';

function FormConfirmEmail() {
  const dispatch = useAppDispatch();
  const { enqueueSnackbar } = useSnackbar();
  const [pin, setPin] = useState<string>('');

  const handlePinChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    // Принимаем только цифры, до 6 символов
    const value = e.target.value;
    if (/^\d{0,6}$/.test(value)) {
      setPin(value);
    }
  };

  const handleRequestPin = () => {
    alert('Запросили пинкод заново (не завезли)');
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (pin.length === 6) {
      // Отправка пинкода на проверку
      dispatch(confirmEmail(pin));
    } else {
      enqueueSnackbar('Введите 6 цифр пинкода', { variant: 'warning' });
    }
  };

  return (
    <Box
      component="form"
      onSubmit={handleSubmit}
      display="flex"
      flexDirection="column"
      alignItems="center"
      width={300}
      mx="auto"
      p={2}
    >
      <Button variant="outlined" color="primary" onClick={handleRequestPin} style={{ marginBottom: 16 }}>
        Запросить пинкод заново
      </Button>
      <TextField
        label="Пинкод"
        variant="outlined"
        value={pin}
        onChange={handlePinChange}
        slotProps={{
          htmlInput: {
            inputMode: 'numeric',
            maxLength: 50,
            pattern: '[0-9]*',
            style: { fontSize: '1.5rem', letterSpacing: '0.3em' },
          },
        }}
        fullWidth
        margin="normal"
      />
      <Button type="submit" variant="contained" color="primary" fullWidth disabled={pin.length !== 6}>
        Отправить пинкод
      </Button>
    </Box>
  );
}

export default FormConfirmEmail;
