import { Box, List, ListItem, ListItemText, Paper, TextField, Typography } from '@mui/material';
import { useEffect, useRef, useState } from 'react';

import { useAppSelector } from '../../hooks/redux';

const MAX_TEXTAREA_HEIGHT_RATIO = 0.5; // max height = 50% of viewport height
const MIN_ROWS = 4;
type Props = {
  readonly chatId: string;
};
function ChatForm({ chatId }: Props) {
  console.log(chatId);
  const { role } = useAppSelector((state) => state.authReducer.user);

  const [messages, setMessages] = useState<string[]>([]);
  const [inputValue, setInputValue] = useState<string>('');
  const chatContainerRef = useRef<HTMLDivElement | null>(null);

  // Отправка сообщения по Enter (без Shift)
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (inputValue.trim()) {
        setMessages((prev) => [...prev, inputValue.trim()]);
        setInputValue('');
      }
    }
  };

  // Автоскролл чата вниз при новых сообщениях
  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [messages]);

  // Максимальная высота TextField (половина экрана)
  const maxHeight = window.innerHeight * MAX_TEXTAREA_HEIGHT_RATIO;

  // Сообщение о типе чата
  const typeChat =
    role === 'anonym'
      ? 'Это обычный чат. Что бы перейти в продвинутый чат войдите на сайт.'
      : 'Вы находитесь в продвинутом чате';

  return (
    <>
      <Box
        ref={chatContainerRef}
        sx={{
          borderBottom: '1px solid #000',
          flexGrow: 1,
          overflowY: 'auto',
          p: 2,
        }}
      >
        <List>
          {messages.length === 0 && (
            <>
              <Typography color="text.secondary" align="center" sx={{ mt: 2 }}>
                {typeChat}
              </Typography>
              <Typography color="text.secondary" align="center" sx={{ mt: 2 }}>
                Здесь будут отображаться ваши сообщения
              </Typography>
            </>
          )}
          {messages.map((msg, index) => (
            <ListItem key={index} disablePadding>
              <Paper
                elevation={1}
                sx={{
                  bgcolor: '#e3f2fd',
                  maxWidth: '80%',
                  mb: 1,
                  p: 1.5,
                  wordBreak: 'break-word',
                }}
              >
                <ListItemText primary={msg} />
              </Paper>
            </ListItem>
          ))}
        </List>
      </Box>

      {/* Поле ввода */}
      <Box
        sx={{
          bgcolor: 'background.paper',
          borderTop: '1px solid #ccc',
          p: 1,
        }}
      >
        <TextField
          multiline
          minRows={MIN_ROWS}
          maxRows={Math.floor(maxHeight / 24)} // приблизительно 24px на строку
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Введите сообщение..."
          fullWidth
          variant="outlined"
          sx={{
            '& .MuiInputBase-root': {
              maxHeight: maxHeight,
              overflow: 'auto',
            },
          }}
        />
      </Box>
    </>
  );
}

export default ChatForm;
