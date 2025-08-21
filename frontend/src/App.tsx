import { useAppDispatch, useAppSelector } from 'hooks/redux';
import { HomePage } from 'pages/Home/HomePage';
import { useEffect } from 'react';
import { Route, Routes } from 'react-router-dom';
import { editCurrentModalOverlay, getCurrentUser } from 'store/reducers/auth/ActionCreators';
import './index.scss';
import { ModalsWrapper } from 'components/Modals/Wrapper/ModalsWrapper';

export const App = () => {
  const { isInitUser, currentModalOverlay } = useAppSelector((state) => state.authReducer);
  const dispatch = useAppDispatch();

  useEffect(() => {
    dispatch(getCurrentUser());
  }, [dispatch]);

  if (!isInitUser) {
    return <div>Загрузка приложения ...</div>;
  }

  const editModal = (value: string | null) => {
    dispatch(editCurrentModalOverlay(value));
  };

  return (
    <div className="container">
      <ModalsWrapper currentModalOverlay={currentModalOverlay} editCurrentModalOverlay={editModal}>
        <Routes>
          <Route path={'/'} element={<HomePage editCurrentModalOverlay={editModal} />} />
        </Routes>
      </ModalsWrapper>
    </div>
  );
};
