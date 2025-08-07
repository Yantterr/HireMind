import '@fontsource/roboto/300.css';
import '@fontsource/roboto/400.css';
import '@fontsource/roboto/500.css';
import '@fontsource/roboto/700.css';

import { createTheme, responsiveFontSizes, ThemeProvider } from '@mui/material/styles';
import { SnackbarProvider } from 'notistack';
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { Provider } from 'react-redux';
import { BrowserRouter } from 'react-router-dom';
import { getCurrentUser } from 'store/reducers/auth/ActionCreators.ts';

import App from './App.tsx';
import store from './store/store';

let theme = createTheme();
theme = responsiveFontSizes(theme);

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <Provider store={store}>
        <ThemeProvider theme={theme}>
          <SnackbarProvider maxSnack={2}>
            <App />
          </SnackbarProvider>
        </ThemeProvider>
      </Provider>
    </BrowserRouter>
  </StrictMode>,
);

store.dispatch(getCurrentUser());
