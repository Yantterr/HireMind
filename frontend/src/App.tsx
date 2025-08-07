import { Box, Container } from '@mui/material';
import CssBaseline from '@mui/material/CssBaseline';
import ChatCreateForm from 'components/CreateChatForm/CreateChatForm';
import MyAppBar from 'components/MyAppBar/MyAppBar';
import { useAppSelector } from 'hooks/redux';
import Chat from 'pages/Chat/Chat';
import ConfirmEmailPage from 'pages/ConfirmEmailPage/ConfirmEmailPage';
import ExamplePage from 'pages/ExamplePage/ExamplePage';
import Home from 'pages/Home/Home';
import Login from 'pages/Login/Login';
import LogoutPage from 'pages/LogoutPage/LogoutPage';
import Page404 from 'pages/Page404/Page404';
import ProfilePage from 'pages/ProfilePage/ProfilePage';
import Register from 'pages/Register/Register';
import { lazy } from 'react';
import { Route, Routes } from 'react-router-dom';
import { Slide, ToastContainer } from 'react-toastify';
import RequireAnonym from 'utils/RequireAnonym/RequireAnonym';
import RequireAuth from 'utils/RequireAuth/RequireAuth';
import withSuspense from 'utils/withSuspense';

const ExampleSuspensePage = lazy(() => import('pages/ExampleSuspensePage/ExampleSuspensePage'));

export default function App() {
  const { isInitUser } = useAppSelector((state) => state.authReducer);

  if (!isInitUser) {
    return <div>Загрузка приложения ...</div>;
  }
  return (
    <>
      <CssBaseline />
      <Container
        maxWidth={false}
        disableGutters
        sx={{
          display: 'flex',
          flexDirection: 'column',
          height: '100vh',
        }}
      >
        <MyAppBar />
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            flexGrow: 1,
            minHeight: 0,
          }}
        >
          <Routes>
            <Route element={<RequireAnonym />}>
              <Route path="login" element={<Login />} />
              <Route path="register" element={<Register />} />
            </Route>
            <Route element={<RequireAuth />}>
              <Route path="profile" element={<ProfilePage />} />
              <Route path="logout" element={<LogoutPage />} />
              <Route path="confirm-email" element={<ConfirmEmailPage />} />

              <Route path="example_route_1" element={<ExamplePage />} />
              <Route path="example_route_2/*" element={withSuspense(ExampleSuspensePage)} />
            </Route>
            <Route path="example_route_3/:recipeId" element={withSuspense(ExampleSuspensePage)} />
            <Route path="example_route_3" element={withSuspense(ExampleSuspensePage)} />
            <Route path="chat/new" element={withSuspense(ChatCreateForm)} />
            <Route path="chat/:chatId" element={withSuspense(Chat)} />

            <Route path="/" element={<Home />} />
            <Route path="*" element={<Page404 />} />
          </Routes>
        </Box>
        <ToastContainer
          position="top-right"
          transition={Slide}
          autoClose={5000}
          hideProgressBar={false}
          newestOnTop={false}
          closeOnClick
          rtl={false}
          pauseOnFocusLoss
          draggable
          pauseOnHover
        />
      </Container>
    </>
  );
}
