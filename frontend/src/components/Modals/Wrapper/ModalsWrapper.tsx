import { useEffect, type ReactElement } from 'react';
import styles from './ModalsWrapper.module.scss';
import { Header } from 'components/Header/Header';
import { useAppDispatch, useAppSelector } from 'hooks/redux';
import { LoginModal } from '../Auth/LoginModal';
import { RegisterModal } from '../Auth/RegisterModal';
import { LogoutModal } from '../Auth/LogoutModal';
import { getNewKey, logoutAuth } from 'store/reducers/auth/ActionCreators';
import { ConfirmEmailModal } from '../Auth/ConfirmEmailModal';
import { CreateChatModal } from '../Chats/CreateChatModal';

type Props = {
  children: ReactElement;
  currentModalOverlay: string | null;
  editCurrentModalOverlay: (value: string | null) => void;
};

export const ModalsWrapper = ({ children, currentModalOverlay, editCurrentModalOverlay }: Props) => {
  const { isFetching: authFetching, user, error: authError } = useAppSelector((state) => state.authReducer);
  const { error: chatsError, isFetching: chatsFetching } = useAppSelector((state) => state.chatsReducer);
  const dispatch = useAppDispatch();

  useEffect(() => {
    editCurrentModalOverlay(null);
  }, [user.role]);

  return (
    <div className={styles.container}>
      <Header
        isActivated={user.isActivated}
        logoutUser={() => editCurrentModalOverlay('logout')}
        username={user.username}
        setCurrentModalOverlay={editCurrentModalOverlay}
      />
      <CreateChatModal
        editCurrentModalOverlay={editCurrentModalOverlay}
        isFetching={chatsFetching}
        chatsError={chatsError}
        isShow={'createChat' === currentModalOverlay}
      />
      {user.role === 'anonym' ? (
        <>
          <LoginModal
            editCurrentModalOverlay={editCurrentModalOverlay}
            isFetching={authFetching}
            authError={authError}
            isShow={currentModalOverlay === 'login'}
          />
          <RegisterModal
            editCurrentModalOverlay={editCurrentModalOverlay}
            isFetching={authFetching}
            authError={authError}
            isShow={currentModalOverlay === 'register'}
          />
        </>
      ) : (
        <>
          <LogoutModal
            logoutUser={() => dispatch(logoutAuth())}
            isFetching={authFetching}
            editCurrentModalOverlay={editCurrentModalOverlay}
            isShow={currentModalOverlay === 'logout'}
          />
          <ConfirmEmailModal
            getNewKey={() => dispatch(getNewKey())}
            editCurrentModalOverlay={editCurrentModalOverlay}
            error={authError}
            isFetching={authFetching}
            isShow={currentModalOverlay === 'confirmEmail' && !user.isActivated}
          />
        </>
      )}
      <div className={`${styles.body} ${currentModalOverlay ? 'blur' : ''}`}>{children}</div>
    </div>
  );
};
