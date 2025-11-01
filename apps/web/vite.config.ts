import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5174, // Changed from 5173 (Docker uses 5173)
    host: true
  },
  build: {
    outDir: 'dist',
    sourcemap: true
  }
})
