import { defineConfig } from 'vite'

export default defineConfig({
  root: '.',
  server: {
    port: 3000,
    open: true,
    cors: true
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: true,
    minify: 'terser',
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['./src/js/utils/api.js'],
          components: ['./src/js/components/auth.js', './src/js/components/navigation.js']
        }
      }
    }
  },
  css: {
    devSourcemap: true
  },
  resolve: {
    alias: {
      '@': '/src',
      '@components': '/src/js/components',
      '@utils': '/src/js/utils',
      '@styles': '/src/css',
      '@assets': '/src/assets'
    }
  }
})