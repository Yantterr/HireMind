import react from '@vitejs/plugin-react';
import tsconfigPaths from 'vite-tsconfig-paths';
import { defineConfig } from 'vitest/config';

// https://vitejs.dev/config/

export default defineConfig({
  plugins: [react(), tsconfigPaths()],
  resolve: {
    alias: {
      src: '/src',
    },
  },
  server: {
    open: true,
    port: 3000,
  },
  test: {
    environment: 'jsdom',
    globals: true,
    mockReset: true,
    setupFiles: 'src/setupTests',
  },
});
