<script setup lang="ts">
import { RouterView } from 'vue-router'
import AppHeader from './components/AppHeader.vue'
</script>

<template>
  <AppHeader />
  <main class="app-main">
    <RouterView />
  </main>
  <footer class="app-footer">
    <div class="container">
      <hr class="rule" />
      <div class="footer-row">
        <span class="footer-text">workbuddy 专题 · 知乎内容聚合知识库</span>
        <span class="footer-text">课程作业项目 · 2026</span>
      </div>
    </div>
  </footer>
</template>

<style scoped>
.app-main {
  min-height: calc(100vh - 56px - 60px);
}
.app-footer {
  padding: 24px 0;
}
.footer-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 0 4px;
  font-family: var(--font-serif);
  font-size: 12px;
  color: var(--ink-4);
}
</style>
