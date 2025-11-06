import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import legacy from '@vitejs/plugin-legacy'
import { resolve } from 'path'

export default defineConfig({
  plugins: [
    vue(),
    legacy({
      targets: ['defaults', 'not IE 11'],
    }),
  ],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  server: {
    port: 3801,
    host: '0.0.0.0',
    proxy: {
      '/api': {
        target: 'http://localhost:9970',
        changeOrigin: true,
      },
    },
  },
})

