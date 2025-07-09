import { TextField } from '@mui/material';
import { useState } from 'react';

type IProps = {
  label: string;
  required?: boolean;
  autoFocus?: boolean;
  type?: string;
  placeholder?: string;
  validator: (value: string) => boolean;
  onChange: (value: string, isValid: boolean) => void;
  sx?: object;
  disabled?: boolean;
};

const ValidatedTextField = ({
  label,
  required = false,
  autoFocus = false,
  type = '',
  placeholder = '',
  validator,
  onChange,
  sx = {},
  disabled = false,
}: IProps) => {
  const [value, setValue] = useState('');
  const [error, setError] = useState(false);
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    const isValid = validator(newValue);
    setValue(newValue);
    setError(!isValid);
    onChange(newValue, isValid);
  };
  return (
    <TextField
      label={label}
      required={required}
      autoFocus={autoFocus}
      value={value}
      onChange={handleChange}
      error={!!error}
      helperText={error}
      fullWidth
      type={type}
      placeholder={placeholder}
      sx={sx}
      disabled={disabled}
    />
  );
};

export default ValidatedTextField;
