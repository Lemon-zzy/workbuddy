// vite.config.ts
import { defineConfig } from "file:///D:/workbuddy%E4%B8%93%E9%A2%98/frontend/node_modules/vite/dist/node/index.js";
import vue from "file:///D:/workbuddy%E4%B8%93%E9%A2%98/frontend/node_modules/@vitejs/plugin-vue/dist/index.mjs";
import path from "path";
var __vite_injected_original_dirname = "D:\\workbuddy\u4E13\u9898\\frontend";
var vite_config_default = defineConfig({
  plugins: [vue()],
  resolve: {
    alias: { "@": path.resolve(__vite_injected_original_dirname, "./src") }
  },
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true
      }
    }
  },
  optimizeDeps: {
    // Windows 下 .vite 缓存被锁，禁用 optimizeDeps 让 Vite 直接走 node_modules
    disabled: true
  }
});
export {
  vite_config_default as default
};
//# sourceMappingURL=data:application/json;base64,ewogICJ2ZXJzaW9uIjogMywKICAic291cmNlcyI6IFsidml0ZS5jb25maWcudHMiXSwKICAic291cmNlc0NvbnRlbnQiOiBbImNvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9kaXJuYW1lID0gXCJEOlxcXFx3b3JrYnVkZHlcdTRFMTNcdTk4OThcXFxcZnJvbnRlbmRcIjtjb25zdCBfX3ZpdGVfaW5qZWN0ZWRfb3JpZ2luYWxfZmlsZW5hbWUgPSBcIkQ6XFxcXHdvcmtidWRkeVx1NEUxM1x1OTg5OFxcXFxmcm9udGVuZFxcXFx2aXRlLmNvbmZpZy50c1wiO2NvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9pbXBvcnRfbWV0YV91cmwgPSBcImZpbGU6Ly8vRDovd29ya2J1ZGR5JUU0JUI4JTkzJUU5JUEyJTk4L2Zyb250ZW5kL3ZpdGUuY29uZmlnLnRzXCI7aW1wb3J0IHsgZGVmaW5lQ29uZmlnIH0gZnJvbSAndml0ZSdcbmltcG9ydCB2dWUgZnJvbSAnQHZpdGVqcy9wbHVnaW4tdnVlJ1xuaW1wb3J0IHBhdGggZnJvbSAncGF0aCdcblxuZXhwb3J0IGRlZmF1bHQgZGVmaW5lQ29uZmlnKHtcbiAgcGx1Z2luczogW3Z1ZSgpXSxcbiAgcmVzb2x2ZToge1xuICAgIGFsaWFzOiB7ICdAJzogcGF0aC5yZXNvbHZlKF9fZGlybmFtZSwgJy4vc3JjJykgfSxcbiAgfSxcbiAgc2VydmVyOiB7XG4gICAgcG9ydDogNTE3MyxcbiAgICBwcm94eToge1xuICAgICAgJy9hcGknOiB7XG4gICAgICAgIHRhcmdldDogJ2h0dHA6Ly8xMjcuMC4wLjE6ODAwMCcsXG4gICAgICAgIGNoYW5nZU9yaWdpbjogdHJ1ZSxcbiAgICAgIH0sXG4gICAgfSxcbiAgfSxcbiAgb3B0aW1pemVEZXBzOiB7XG4gICAgLy8gV2luZG93cyBcdTRFMEIgLnZpdGUgXHU3RjEzXHU1QjU4XHU4OEFCXHU5NTAxXHVGRjBDXHU3OTgxXHU3NTI4IG9wdGltaXplRGVwcyBcdThCQTkgVml0ZSBcdTc2RjRcdTYzQTVcdThENzAgbm9kZV9tb2R1bGVzXG4gICAgZGlzYWJsZWQ6IHRydWUsXG4gIH0sXG59KVxuIl0sCiAgIm1hcHBpbmdzIjogIjtBQUE2USxTQUFTLG9CQUFvQjtBQUMxUyxPQUFPLFNBQVM7QUFDaEIsT0FBTyxVQUFVO0FBRmpCLElBQU0sbUNBQW1DO0FBSXpDLElBQU8sc0JBQVEsYUFBYTtBQUFBLEVBQzFCLFNBQVMsQ0FBQyxJQUFJLENBQUM7QUFBQSxFQUNmLFNBQVM7QUFBQSxJQUNQLE9BQU8sRUFBRSxLQUFLLEtBQUssUUFBUSxrQ0FBVyxPQUFPLEVBQUU7QUFBQSxFQUNqRDtBQUFBLEVBQ0EsUUFBUTtBQUFBLElBQ04sTUFBTTtBQUFBLElBQ04sT0FBTztBQUFBLE1BQ0wsUUFBUTtBQUFBLFFBQ04sUUFBUTtBQUFBLFFBQ1IsY0FBYztBQUFBLE1BQ2hCO0FBQUEsSUFDRjtBQUFBLEVBQ0Y7QUFBQSxFQUNBLGNBQWM7QUFBQTtBQUFBLElBRVosVUFBVTtBQUFBLEVBQ1o7QUFDRixDQUFDOyIsCiAgIm5hbWVzIjogW10KfQo=
