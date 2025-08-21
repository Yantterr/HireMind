import { useForm } from 'react-hook-form';
import styles from '../Modal.module.scss';
import { useState } from 'react';
import eye from '../../../assets/imgs/eye.svg';
import { validatePassword } from 'utils/auth';
import { useAppDispatch } from 'hooks/redux';
import { registerAuth } from 'store/reducers/auth/ActionCreators';

type Props = {
  isShow: boolean;
  authError?: string;
  isFetching: boolean;
  editCurrentModalOverlay: (value: string | null) => void;
};

type FormData = {
  email: string;
  password: string;
  repeat_password: string;
  username: string;
};

export const RegisterModal = ({ isShow, editCurrentModalOverlay, isFetching, authError }: Props) => {
  const [isShowPassword, setIsShowPassword] = useState<boolean>(false);
  const [isShowRepeatPassword, setIsShowRepeatPassword] = useState<boolean>(false);
  const dispatch = useAppDispatch();

  const {
    register,
    handleSubmit,
    watch,
    formState: { isSubmitting, errors },
  } = useForm<FormData>();

  const onSubmit = async (value: FormData) => {
    dispatch(registerAuth(value.email, value.password, value.username, () => editCurrentModalOverlay('confirmEmail')));
  };

  return (
    <div className={styles.container} style={{ bottom: isShow ? '50%' : '150%' }}>
      <div className={styles.wrapper}>
        <button
          className={`${styles.close} ${isFetching || isSubmitting ? `${styles.close_disabled} fetching` : ''}`}
          type="button"
          disabled={isSubmitting || isFetching}
          onClick={() => editCurrentModalOverlay(null)}
        ></button>
        <h2 style={{ fontSize: '46px' }} className={styles.title}>
          Регистрация
        </h2>
        <form className={styles.form} onSubmit={handleSubmit(onSubmit)}>
          <div className={styles.input}>
            <input
              placeholder="Email"
              type="email"
              {...register('email', {
                required: true,
                pattern: {
                  value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                  message: 'Некорректный email',
                },
              })}
            />
            {errors.email && <div className={styles.error}>{errors.email.message}</div>}
          </div>
          <div className={styles.input}>
            <input placeholder="Username" {...register('username', { required: true })} />
            {errors.username && <div className={styles.error}>{errors.username.message}</div>}
          </div>

          <div className={`${styles.password} ${styles.input}`}>
            <input
              type={isShowPassword ? 'text' : 'password'}
              placeholder="Пароль"
              {...register('password', { required: true, validate: validatePassword })}
            />
            <div className={styles.eye} onClick={() => setIsShowPassword(!isShowPassword)}>
              <img src={eye} alt="eye" />
              <span style={{ scale: isShowPassword ? '0' : '1' }}></span>
            </div>
            {errors.password && <div className={styles.error}>{errors.password.message}</div>}
          </div>
          <div className={`${styles.input} ${styles.password}`}>
            <input
              type={isShowRepeatPassword ? 'text' : 'password'}
              placeholder="Повторите пароль"
              {...register('repeat_password', {
                required: true,
                validate: (value) => value === watch('password') || 'Пароли не совпадают',
              })}
            />
            <div className={styles.eye} onClick={() => setIsShowRepeatPassword(!isShowRepeatPassword)}>
              <img src={eye} alt="eye" />
              <span style={{ scale: isShowRepeatPassword ? '0' : '1' }}></span>
            </div>
            {errors.repeat_password && <div className={styles.error}>{errors.repeat_password.message}</div>}
          </div>
          <div className={styles.auth}>
            <button
              className={`${styles.button} ${isFetching ? `${styles.button_active} fetching` : ''}`}
              type="submit"
              disabled={isSubmitting}
            >
              Зарегистрироваться
            </button>
            {authError && <div className={`${styles.auth_error} ${styles.error}`}>{authError}</div>}
          </div>
        </form>
      </div>
    </div>
  );
};
