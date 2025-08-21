export const validatePassword = (password: string) => {
  const PASSWORD_DIGIT_PATTERN = /\d/;
  const PASSWORD_UPPERCASE_PATTERN = /[A-Z]/;
  const PASSWORD_LOWERCASE_PATTERN = /[a-z]/;
  const PASSWORD_SPECIAL_PATTERN = /[!@#$%^&*()_+\-=[\]{};':"\\|,.<>/?]/;

  if (password.length < 12) {
    return 'Минимум 12 символов';
  }

  if (password.includes(' ')) {
    return 'Пароль не должен содержать пробелы';
  }

  const validations = [
    {
      pattern: PASSWORD_DIGIT_PATTERN,
      message: 'минимум одну цифру (0-9)',
    },
    {
      pattern: PASSWORD_UPPERCASE_PATTERN,
      message: 'минимум одну заглавную букву (A-Z, А-Я)',
    },
    {
      pattern: PASSWORD_LOWERCASE_PATTERN,
      message: 'минимум одну строчную букву (a-z, а-я)',
    },
    {
      pattern: PASSWORD_SPECIAL_PATTERN,
      message: 'минимум один специальный символ (!@#$%^&* и т.д.)',
    },
  ];

  for (const { pattern, message } of validations) {
    if (!pattern.test(password)) {
      return `Пароль должен содержать ${message}`;
    }
  }

  return true;
};
