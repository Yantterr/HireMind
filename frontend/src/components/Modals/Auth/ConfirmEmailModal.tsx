import { useForm } from 'react-hook-form';
import styles from '../Modal.module.scss';
import { useAppDispatch } from 'hooks/redux';
import { confirmEmail } from 'store/reducers/auth/ActionCreators';

type Props = {
  isShow: boolean;
  isFetching: boolean;
  error?: string;
  getNewKey: () => void;
  editCurrentModalOverlay: (value: string | null) => void;
};

type FormData = {
  key: string;
};

export const ConfirmEmailModal = ({ isShow, editCurrentModalOverlay, getNewKey, error, isFetching }: Props) => {
  const dispatch = useAppDispatch();

  const {
    register,
    handleSubmit,
    setValue,
    getValues,
    formState: { isSubmitting, errors },
  } = useForm<FormData>({
    defaultValues: {
      key: '',
    },
  });

  const onSubmit = async (value: FormData) => {
    dispatch(confirmEmail(Number(value.key)));
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const numericValue = e.target.value.replace(/\D/g, '');

    if (numericValue.length > 6) {
      return;
    }

    setValue('key', numericValue, { shouldValidate: true });
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
        <h2 className={styles.title} style={{ fontSize: '33px' }}>
          Подтверждение почты
        </h2>
        <form onSubmit={handleSubmit(onSubmit)} className={styles.form}>
          <div className={styles.input}>
            <input
              value={getValues('key')}
              type="text"
              inputMode="numeric"
              placeholder="Pin-code"
              {...register('key', {
                required: 'Поле обязательно для заполнения',
                pattern: {
                  value: /^[0-9]{6}$/,
                  message: 'Некорректный pin-code (6 цифр)',
                },
              })}
              onChange={handleInputChange}
            />
            {errors.key && <div className={styles.error}>{errors.key.message}</div>}
          </div>
          <button
            className={`${styles.button} ${isFetching ? `${styles.button_active} fetching` : ''}`}
            type="submit"
            disabled={isSubmitting}
          >
            Подтвердить
          </button>
          <button
            onClick={getNewKey}
            type="button"
            className={`${styles.button} ${isFetching ? `${styles.button_active} fetching` : ''}`}
          >
            Получить новый код
          </button>
          {error && (
            <div className={`${styles.auth_error} ${styles.error}`} style={{ marginTop: '0px' }}>
              {error}
            </div>
          )}
        </form>
      </div>
    </div>
  );
};
