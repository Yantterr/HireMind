import { Link } from 'react-router-dom';
import styles from './Header.module.scss';
import logout_icon from '../../assets/imgs/logout.svg';

type Props = {
  username?: string;
  isActivated: boolean;
  setCurrentModalOverlay: (value: string | null) => void;
  logoutUser: () => void;
};

export const Header = ({ username, isActivated, setCurrentModalOverlay }: Props) => {
  return (
    <div className={styles.container}>
      <Link to={'/'} className={styles.title}>
        HireMind
      </Link>
      {username ? (
        <div className={styles.user}>
          {!isActivated ? (
            <button
              className={`${styles.button} ${styles.button_dark}`}
              onClick={() => setCurrentModalOverlay('confirmEmail')}
            >
              Подтвердить почту
            </button>
          ) : (
            <div className={styles.username}>{username}</div>
          )}
          <div className={styles.logout} onClick={() => setCurrentModalOverlay('logout')}>
            <img src={logout_icon} alt="logout" />
          </div>
        </div>
      ) : (
        <div className={styles.buttons}>
          <button
            onClick={() => setCurrentModalOverlay('register')}
            className={`${styles.button} ${styles.button_dark}`}
          >
            Регистрация
          </button>
          <button onClick={() => setCurrentModalOverlay('login')} className={`${styles.button} ${styles.button_light}`}>
            Вход
          </button>
        </div>
      )}
    </div>
  );
};
