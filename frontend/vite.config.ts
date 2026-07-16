import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  root: __dirname,
  plugins: [vue()],
  resolve: {
    alias: { '@': path.resolve(__dirname, './src') },
  },
  server: {
    port: 5173,
    host: '127.0.0.1',
    strictPort: true,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
  optimizeDeps: {
    // Windows 下 .vite 缓存被锁，跳过 deps 预构建
    noDiscovery: true,
    include: [],
    entries: ['index.html'],
  },
})
