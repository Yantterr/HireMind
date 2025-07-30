import CancelIcon from '@mui/icons-material/Cancel';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import { Box, Button, Chip, Grid, Typography } from '@mui/material';
import { useAppSelector } from 'hooks/redux';
import { useNavigate } from 'react-router-dom';

export default function ProfilePage() {
  const navigate = useNavigate();

  const { user } = useAppSelector((state) => state.authReducer);

  const handleActivate = () => {
    navigate('/confirm-email'); // путь на страницу активации
  };

  return (
    <Box
      sx={{
        bgcolor: 'background.paper',
        margin: 'auto',
        maxWidth: 700,
        mt: 1,
        p: 4,
      }}
    >
      <Typography variant="h4" gutterBottom align="center">
        Профиль пользователя
      </Typography>
      <Grid container spacing={4}>
        <Grid sx={{ sm: 6, xs: 12 }} size={{ sm: 6, xs: 12 }}>
          <Typography variant="h6">Логин:</Typography>
        </Grid>
        <Grid sx={{ sm: 6, xs: 12 }} size={{ sm: 6, xs: 12 }}>
          <Typography variant="body1">{user.login}</Typography>
        </Grid>
        <Grid sx={{ sm: 6, xs: 12 }} size={{ sm: 6, xs: 12 }}>
          <Typography variant="h6">E-mail:</Typography>
        </Grid>
        <Grid sx={{ sm: 6, xs: 12 }} size={{ sm: 6, xs: 12 }}>
          <Typography variant="body1">{user.email}</Typography>
        </Grid>
        <Grid sx={{ sm: 6, xs: 12 }} size={{ sm: 6, xs: 12 }}>
          <Typography variant="h6">Почта подтверждена:</Typography>
        </Grid>
        <Grid sx={{ sm: 6, xs: 12 }} size={{ sm: 6, xs: 12 }}>
          {user.isActivated ? (
            <Chip label="Да" icon={<CheckCircleIcon color="success" />} color="success" variant="outlined" />
          ) : (
            <Chip label="Нет" icon={<CancelIcon color="error" />} color="error" variant="outlined" />
          )}
        </Grid>
        <Grid sx={{ display: 'flex', justifyContent: 'center', sm: 6, xs: 12 }} size={12}>
          {!user.isActivated && (
            <Button variant="contained" color="primary" onClick={handleActivate} startIcon={<CheckCircleIcon />}>
              Подтвердить почту
            </Button>
          )}
        </Grid>
      </Grid>
    </Box>
  );
}
