import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// The frontend calls "/api/..." and Vite proxies that to Django, so in development
// the browser only ever talks to one origin and CORS never enters the picture.
// Point VITE_BACKEND_URL at the backend if you run it somewhere other than :8000.
const BACKEND = process.env.VITE_BACKEND_URL || 'http://127.0.0.1:8000'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    strictPort: true,
    proxy: {
      '/api': {
        target: BACKEND,
        changeOrigin: true,
      },
    },
  },
})
