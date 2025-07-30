import { Box, Button, Typography } from '@mui/material';
import { useNavigate } from 'react-router-dom';

type Props = {
  readonly chatId: undefined | string;
};

function UnknownChat({ chatId }: Props) {
  const navigate = useNavigate();

  return (
    <Box
      sx={{
        alignItems: 'center',
        display: 'flex',
        flexDirection: 'column',
        height: '100vh',
        justifyContent: 'center',
        p: 2,
      }}
    >
      <Box
        sx={{
          border: '2px solid red', // красная рамка
          borderRadius: 2,
          minWidth: 300,
          p: 4,
          textAlign: 'center',
        }}
      >
        <Typography variant="h6" color="error" gutterBottom>
          Неопознанный чат!
        </Typography>
        {chatId && (
          <Typography variant="h6" color="error" gutterBottom>
            Id чата = [{chatId}]
          </Typography>
        )}
        <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', mt: 3 }}>
          <Button variant="outlined" color="error" onClick={() => navigate(-1)}>
            Вернуться назад
          </Button>

          <Button variant="contained" color="error" onClick={() => navigate('/new-chat')}>
            Создать новый чат
          </Button>
        </Box>
      </Box>
    </Box>
  );
}

export default UnknownChat;
