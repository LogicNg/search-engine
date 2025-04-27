import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  //set proxy to backend
  server: {
    proxy: {
      '/search': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
      },
    },
  },
})
