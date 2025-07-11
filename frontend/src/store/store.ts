import { combineReducers, configureStore } from '@reduxjs/toolkit';

import authReducer from './reducers/auth/Slice';

const rootReducer = combineReducers({
  authReducer,
});

export const setupStore = () => {
  return configureStore({
    reducer: rootReducer,
    // middleware: (getDefaultMiddleware) => getDefaultMiddleware().concat(postAPI.middleware),
  });
};

export type RootState = ReturnType<typeof rootReducer>;
export type AppStore = ReturnType<typeof setupStore>;
export type AppDispatch = AppStore['dispatch'];
const store = setupStore();
export default store;
