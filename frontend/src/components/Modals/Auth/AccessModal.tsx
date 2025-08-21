import styles from './Modal.module.scss';

type Props = {
  isShow: boolean;
};

export const AccessModal = ({ isShow }: Props) => {
  return (
    <div className={styles.container} style={{ bottom: isShow ? '50%' : '150%' }}>
      <div className={styles.wrapper}>
        <h2 className={styles.title}>Вход</h2>
      </div>
    </div>
  );
};
