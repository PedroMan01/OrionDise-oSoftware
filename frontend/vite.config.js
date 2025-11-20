import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    host: true,     // ← Esto permite acceso desde IPs externas como ngrok
    port: 5173      // ← Puedes cambiarlo si quieres otro puerto
  }
});

