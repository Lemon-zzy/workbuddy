// vite.config.ts
import { defineConfig } from "file:///D:/workbuddy%E4%B8%93%E9%A2%98/frontend/node_modules/vite/dist/node/index.js";
import vue from "file:///D:/workbuddy%E4%B8%93%E9%A2%98/frontend/node_modules/@vitejs/plugin-vue/dist/index.mjs";
import path from "path";
var __vite_injected_original_dirname = "D:\\workbuddy\u4E13\u9898\\frontend";
var vite_config_default = defineConfig({
  root: __vite_injected_original_dirname,
  plugins: [vue()],
  resolve: {
    alias: { "@": path.resolve(__vite_injected_original_dirname, "./src") }
  },
  server: {
    port: 5173,
    host: "127.0.0.1",
    strictPort: true,
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true
      }
    }
  },
  optimizeDeps: {
    // Windows 下 .vite 缓存被锁，跳过 deps 预构建
    noDiscovery: true,
    include: [],
    entries: ["index.html"]
  }
});
export {
  vite_config_default as default
};
//# sourceMappingURL=data:application/json;base64,ewogICJ2ZXJzaW9uIjogMywKICAic291cmNlcyI6IFsidml0ZS5jb25maWcudHMiXSwKICAic291cmNlc0NvbnRlbnQiOiBbImNvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9kaXJuYW1lID0gXCJEOlxcXFx3b3JrYnVkZHlcdTRFMTNcdTk4OThcXFxcZnJvbnRlbmRcIjtjb25zdCBfX3ZpdGVfaW5qZWN0ZWRfb3JpZ2luYWxfZmlsZW5hbWUgPSBcIkQ6XFxcXHdvcmtidWRkeVx1NEUxM1x1OTg5OFxcXFxmcm9udGVuZFxcXFx2aXRlLmNvbmZpZy50c1wiO2NvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9pbXBvcnRfbWV0YV91cmwgPSBcImZpbGU6Ly8vRDovd29ya2J1ZGR5JUU0JUI4JTkzJUU5JUEyJTk4L2Zyb250ZW5kL3ZpdGUuY29uZmlnLnRzXCI7aW1wb3J0IHsgZGVmaW5lQ29uZmlnIH0gZnJvbSAndml0ZSdcbmltcG9ydCB2dWUgZnJvbSAnQHZpdGVqcy9wbHVnaW4tdnVlJ1xuaW1wb3J0IHBhdGggZnJvbSAncGF0aCdcblxuZXhwb3J0IGRlZmF1bHQgZGVmaW5lQ29uZmlnKHtcbiAgcm9vdDogX19kaXJuYW1lLFxuICBwbHVnaW5zOiBbdnVlKCldLFxuICByZXNvbHZlOiB7XG4gICAgYWxpYXM6IHsgJ0AnOiBwYXRoLnJlc29sdmUoX19kaXJuYW1lLCAnLi9zcmMnKSB9LFxuICB9LFxuICBzZXJ2ZXI6IHtcbiAgICBwb3J0OiA1MTczLFxuICAgIGhvc3Q6ICcxMjcuMC4wLjEnLFxuICAgIHN0cmljdFBvcnQ6IHRydWUsXG4gICAgcHJveHk6IHtcbiAgICAgICcvYXBpJzoge1xuICAgICAgICB0YXJnZXQ6ICdodHRwOi8vMTI3LjAuMC4xOjgwMDAnLFxuICAgICAgICBjaGFuZ2VPcmlnaW46IHRydWUsXG4gICAgICB9LFxuICAgIH0sXG4gIH0sXG4gIG9wdGltaXplRGVwczoge1xuICAgIC8vIFdpbmRvd3MgXHU0RTBCIC52aXRlIFx1N0YxM1x1NUI1OFx1ODhBQlx1OTUwMVx1RkYwQ1x1OERGM1x1OEZDNyBkZXBzIFx1OTg4NFx1Njc4NFx1NUVGQVxuICAgIG5vRGlzY292ZXJ5OiB0cnVlLFxuICAgIGluY2x1ZGU6IFtdLFxuICAgIGVudHJpZXM6IFsnaW5kZXguaHRtbCddLFxuICB9LFxufSlcbiJdLAogICJtYXBwaW5ncyI6ICI7QUFBNlEsU0FBUyxvQkFBb0I7QUFDMVMsT0FBTyxTQUFTO0FBQ2hCLE9BQU8sVUFBVTtBQUZqQixJQUFNLG1DQUFtQztBQUl6QyxJQUFPLHNCQUFRLGFBQWE7QUFBQSxFQUMxQixNQUFNO0FBQUEsRUFDTixTQUFTLENBQUMsSUFBSSxDQUFDO0FBQUEsRUFDZixTQUFTO0FBQUEsSUFDUCxPQUFPLEVBQUUsS0FBSyxLQUFLLFFBQVEsa0NBQVcsT0FBTyxFQUFFO0FBQUEsRUFDakQ7QUFBQSxFQUNBLFFBQVE7QUFBQSxJQUNOLE1BQU07QUFBQSxJQUNOLE1BQU07QUFBQSxJQUNOLFlBQVk7QUFBQSxJQUNaLE9BQU87QUFBQSxNQUNMLFFBQVE7QUFBQSxRQUNOLFFBQVE7QUFBQSxRQUNSLGNBQWM7QUFBQSxNQUNoQjtBQUFBLElBQ0Y7QUFBQSxFQUNGO0FBQUEsRUFDQSxjQUFjO0FBQUE7QUFBQSxJQUVaLGFBQWE7QUFBQSxJQUNiLFNBQVMsQ0FBQztBQUFBLElBQ1YsU0FBUyxDQUFDLFlBQVk7QUFBQSxFQUN4QjtBQUNGLENBQUM7IiwKICAibmFtZXMiOiBbXQp9Cg==
