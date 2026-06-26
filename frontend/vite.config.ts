import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const apiTarget = env.VITE_API_PROXY_TARGET || 'http://127.0.0.1:8000'
  const appBase = env.VITE_APP_BASE || '/'

  return {
    base: appBase,
    plugins: [vue()],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url)),
      },
    },
    server: {
      host: '127.0.0.1',
      port: 5173,
      proxy: {
        '/api': {
          target: apiTarget,
          changeOrigin: true,
        },
      },
    },
    build: {
      sourcemap: false,
      chunkSizeWarningLimit: 1500,
      rollupOptions: {
        output: {
          manualChunks(id) {
            const normalizedId = id.replace(/\\/g, '/')
            if (!normalizedId.includes('/node_modules/')) {
              return
            }
            if (
              normalizedId.includes('/node_modules/vue') ||
              normalizedId.includes('/node_modules/vue-router') ||
              normalizedId.includes('/node_modules/pinia')
            ) {
              return 'vue-vendor'
            }
            if (
              normalizedId.includes('/node_modules/element-plus') ||
              normalizedId.includes('/node_modules/@element-plus/icons-vue')
            ) {
              return 'element-vendor'
            }
            if (normalizedId.includes('/node_modules/echarts')) {
              return 'echarts-vendor'
            }
          },
        },
      },
    },
    css: {
      preprocessorOptions: {
        scss: {
          api: 'modern-compiler',
        },
      },
    },
  }
})
