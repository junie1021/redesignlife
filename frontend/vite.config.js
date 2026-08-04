import { fileURLToPath } from 'node:url'
import { defineConfig, loadEnv } from 'vite'
import tailwindcss from '@tailwindcss/vite'

const envDir = fileURLToPath(new URL('../..', import.meta.url))

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, envDir, 'VITE_')
  const apiTarget = env.VITE_API_PROXY_TARGET || 'http://127.0.0.1:8000'
  const proxyOptions = {
    target: apiTarget,
    changeOrigin: true,
  }

  return {
    envDir,
    plugins: [
      tailwindcss(),
    ],
    server: {
      host: '0.0.0.0',
      port: 5173,
      proxy: {
        '/api': { ...proxyOptions },
        '/health': { ...proxyOptions },
        '/docs': { ...proxyOptions },
        '/redoc': { ...proxyOptions },
        '/openapi.json': { ...proxyOptions },
      },
    },
  }
})
