import { Box, Button, Typography } from '@mui/material';
import { teal } from '@mui/material/colors';
import { useNavigate } from 'react-router-dom';

const primary = teal[400]; // #f44336

export default function Page404() {
  const navigate = useNavigate();
  return (
    <Box
      sx={{
        alignItems: 'center',
        backgroundColor: primary,
        display: 'flex',
        flexDirection: 'column',
        flexGrow: 1,
        justifyContent: 'center',
      }}
    >
      <Typography variant="h1" style={{ color: 'white' }}>
        404
      </Typography>
      <Typography variant="h6" style={{ color: 'white', textAlign: 'center' }}>
        Страница, которую вы пытаетесь открыть ну существует.
      </Typography>
      <Button variant="contained" onClick={() => navigate('/')} sx={{ mt: 2 }}>
        На главную
      </Button>
    </Box>
  );
}
