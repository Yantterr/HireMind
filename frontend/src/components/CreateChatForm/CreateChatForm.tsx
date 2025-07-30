import {
  Box,
  Button,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  type SelectChangeEvent,
  Slider,
  TextField,
  Typography,
} from '@mui/material';
import { Controller, useForm } from 'react-hook-form';

interface ChatCreateFormInputs {
  title: string;
  initialContext: string;
  progressionType: number;
  difficulty: number;
  politeness: number;
  friendliness: number;
  rigidity: number;
  detailOrientation: number;
  pacing: number;
  language: string;
}

// Предположим, шкала рейтингов от 1 до 5
const ratingMarks = [
  { label: '1', value: 1 },
  { label: '2', value: 2 },
  { label: '3', value: 3 },
  { label: '4', value: 4 },
  { label: '5', value: 5 },
];

// Пример языков для селекта, можно расширить
const languages = [
  { label: 'Русский', value: 'ru' },
  { label: 'English', value: 'en' },
  { label: 'Spanish', value: 'es' },
  { label: 'French', value: 'fr' },
  { label: 'German', value: 'de' },
];

function ChatCreateForm() {
  const { control, handleSubmit } = useForm<ChatCreateFormInputs>({
    defaultValues: {
      detailOrientation: 3,
      difficulty: 3,
      friendliness: 3,
      initialContext: '',
      language: 'ru',
      pacing: 3,
      politeness: 3,
      progressionType: 3,
      rigidity: 3,
      title: '',
    },
  });

  const onSubmit = (data: ChatCreateFormInputs) => {
    console.log('Создаем чат с параметрами:', data);
    // Здесь отправляйте данные на сервер, например через fetch/axios
    // После успешного создания можно очистить форму:
    // reset();
  };

  return (
    <Box
      maxWidth={600}
      mx="auto"
      mt={4}
      p={3}
      boxShadow={3}
      borderRadius={2}
      component="form"
      onSubmit={handleSubmit(onSubmit)}
    >
      <Typography variant="h5" mb={3} textAlign="center">
        Создание нового чата
      </Typography>

      {/* Заголовок */}
      <Controller
        name="title"
        control={control}
        rules={{ required: 'Введите название' }}
        render={({ field, fieldState }) => (
          <TextField
            {...field}
            label="Название чата"
            fullWidth
            margin="normal"
            error={!!fieldState.error}
            helperText={fieldState.error ? fieldState.error.message : null}
            required
          />
        )}
      />

      {/* Начальный контекст */}
      <Controller
        name="initialContext"
        control={control}
        render={({ field }) => (
          <TextField
            {...field}
            label="Начальный контекст (необязательно)"
            fullWidth
            margin="normal"
            multiline
            minRows={3}
          />
        )}
      />

      {/* Функция для рендеринга слайдеров рейтингов */}
      {[
        { label: 'Тип прогрессии', name: 'progressionType' },
        { label: 'Сложность', name: 'difficulty' },
        { label: 'Вежливость', name: 'politeness' },
        { label: 'Дружелюбие', name: 'friendliness' },
        { label: 'Жесткость', name: 'rigidity' },
        { label: 'Детализированность', name: 'detailOrientation' },
        { label: 'Темп', name: 'pacing' },
      ].map(({ name, label }) => (
        <Controller
          key={name}
          name={name as keyof ChatCreateFormInputs}
          control={control}
          render={({ field }) => (
            <Box my={2}>
              <Typography gutterBottom>
                {label}: {field.value}
              </Typography>
              <Slider
                {...field}
                value={typeof field.value === 'number' ? field.value : 0}
                onChange={(_, value) => field.onChange(value)}
                step={1}
                marks={ratingMarks}
                min={1}
                max={5}
                valueLabelDisplay="auto"
              />
            </Box>
          )}
        />
      ))}

      {/* Язык */}
      <Controller
        name="language"
        control={control}
        render={({ field }) => (
          <FormControl fullWidth margin="normal">
            <InputLabel id="language-select-label">Язык</InputLabel>
            <Select
              {...field}
              labelId="language-select-label"
              label="Язык"
              onChange={(e: SelectChangeEvent) => field.onChange(e.target.value)}
            >
              {languages.map(({ value, label }) => (
                <MenuItem key={value} value={value}>
                  {label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        )}
      />

      <Box mt={4} textAlign="center">
        <Button variant="contained" color="primary" type="submit" size="large">
          Создать чат
        </Button>
      </Box>
    </Box>
  );
}

export default ChatCreateForm;
