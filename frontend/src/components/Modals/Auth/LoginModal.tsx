import { useForm } from 'react-hook-form';
import styles from '../Modal.module.scss';
import { useState } from 'react';
import eye from '../../../assets/imgs/eye.svg';
import { validatePassword } from 'utils/auth';
import { useAppDispatch } from 'hooks/redux';
import { loginAuth } from 'store/reducers/auth/ActionCreators';

type Props = {
  isShow: boolean;
  authError?: string;
  isFetching: boolean;
  editCurrentModalOverlay: (value: string | null) => void;
};

type FormData = {
  email: string;
  password: string;
};

export const LoginModal = ({ isShow, editCurrentModalOverlay, isFetching, authError }: Props) => {
  const [isShowPassword, setIsShowPassword] = useState<boolean>(false);
  const dispatch = useAppDispatch();

  const {
    register,
    handleSubmit,
    formState: { isSubmitting, errors },
  } = useForm<FormData>();

  const onSubmit = async (value: FormData) => {
    dispatch(loginAuth(value.email, value.password));
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
        <h2 className={styles.title}>Вход</h2>
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
          <div className={styles.auth}>
            <button
              className={`${styles.button} ${isFetching ? `${styles.button_active} fetching` : ''}`}
              type="submit"
              disabled={isSubmitting || isFetching}
            >
              Войти
            </button>
            {authError && <div className={`${styles.auth_error} ${styles.error}`}>{authError}</div>}
          </div>
        </form>
      </div>
    </div>
  );
};
