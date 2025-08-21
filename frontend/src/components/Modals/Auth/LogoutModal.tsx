import styles from '../Modal.module.scss';

type Props = {
  isShow: boolean;
  editCurrentModalOverlay: (value: string | null) => void;
  isFetching: boolean;
  logoutUser: () => void;
};

export const LogoutModal = ({ isShow, logoutUser, isFetching, editCurrentModalOverlay }: Props) => {
  return (
    <div className={styles.container} style={{ bottom: isShow ? '50%' : '150%' }}>
      <div className={styles.wrapper}>
        <button
          className={`${styles.close} ${isFetching ? `${styles.close_disabled} fetching` : ''}`}
          type="button"
          disabled={isFetching}
          onClick={() => editCurrentModalOverlay(null)}
        ></button>
        <h2 className={styles.title}>Выйти</h2>
        <div className={styles.buttons}>
          <button className={`${styles.button}`} onClick={() => editCurrentModalOverlay(null)}>
            Отмена
          </button>
          <button
            onClick={logoutUser}
            className={`${styles.button} ${isFetching ? `${styles.button_active} fetching` : ''}`}
          >
            Подтвердить
          </button>
        </div>
      </div>
    </div>
  );
};
