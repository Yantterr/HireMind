import { SnackbarProvider } from 'notistack';
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { Provider } from 'react-redux';
import { BrowserRouter } from 'react-router-dom';
import { getCurrentUser } from 'store/reducers/auth/ActionCreators.ts';

import { App } from './App.tsx';
import store from './store/store';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <Provider store={store}>
        <SnackbarProvider maxSnack={2}>
          <App />
        </SnackbarProvider>
      </Provider>
    </BrowserRouter>
  </StrictMode>,
);

store.dispatch(getCurrentUser());
