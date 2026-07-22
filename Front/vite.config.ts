import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import path from "path";

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  build: {
    target: "esnext",
    cssMinify: true,
    // Code splitting для лучшей производительности
    rollupOptions: {
      output: {
        manualChunks: {
          // Выносим vendor библиотеки в отдельные chunks
          "vendor-vue": ["vue", "vue-router", "pinia"],
          "vendor-axios": ["axios"],
        },
        // Разделяем ассеты по типам
        assetFileNames: (assetInfo) => {
          if (assetInfo.name?.endsWith(".css")) {
            return "assets/css/[name]-[hash][extname]";
          }
          return "assets/[name]-[hash][extname]";
        },
        chunkFileNames: "assets/js/[name]-[hash].js",
        entryFileNames: "assets/js/[name]-[hash].js",
      },
    },
    // Минимизация размера бандла
    minify: "terser",
    // Размер предупреждения
    chunkSizeWarningLimit: 500,
  },
  // Оптимизация dev сервера
  server: {
    host: "0.0.0.0",
    port: 5000,
    allowedHosts: true,
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
      },
      "/media": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
      },
    },
    hmr: {
      overlay: false,
    },
    // Улучшение скорости dev сервера
    warmup: {
      clientFiles: ["./src/main.ts", "./src/App.vue", "./src/router/index.ts"],
    },
  },
  // Оптимизация зависимостей - prebundle для быстрой загрузки
  optimizeDeps: {
    include: ["vue", "vue-router", "pinia", "axios", "vue-i18n"],
    // Исключаем большие файлы из трансформации
    exclude: [],
  },
});
