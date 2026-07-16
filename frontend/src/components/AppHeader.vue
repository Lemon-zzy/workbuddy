<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter, RouterLink } from 'vue-router'
import { computed } from 'vue'

const route = useRoute()
const router = useRouter()
const isActive = (path: string) => computed(() => route.path === path)

// 顶部搜索框
const searchKeyword = ref('')
const submitSearch = () => {
  const kw = searchKeyword.value.trim()
  if (kw) {
    router.push({ name: 'list', query: { keyword: kw } })
  } else {
    router.push({ name: 'list' })
  }
}
</script>

<template>
  <header class="masthead">
    <div class="container masthead-inner">
      <RouterLink to="/" class="brand">
        <span class="brand-name">workbuddy 专题</span>
        <span class="brand-sub">知乎内容聚合 · 学术索引</span>
      </RouterLink>
      <nav class="nav">
        <RouterLink to="/" class="nav-link" :class="{ active: isActive('/').value }">首页</RouterLink>
        <RouterLink to="/list" class="nav-link" :class="{ active: isActive('/list').value }">索引</RouterLink>
        <RouterLink to="/authors" class="nav-link" :class="{ active: isActive('/authors').value || isActive('/author').value }">作者</RouterLink>
        <RouterLink to="/md" class="nav-link" :class="{ active: isActive('/md').value }">文库</RouterLink>
      </nav>
    </div>
    <hr class="rule" />
  </header>
</template>

<style scoped>
.masthead {
  background: var(--paper);
  position: sticky;
  top: 0;
  z-index: 50;
}
.masthead-inner {
  height: var(--header-h);
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.brand {
  display: flex;
  align-items: baseline;
  gap: 14px;
  border: none !important;
}
.brand:hover { border: none !important; }
.brand-name {
  font-family: var(--font-serif);
  font-size: 19px;
  font-weight: 700;
  color: var(--ink-1);
  letter-spacing: 0;
}
.brand-sub {
  font-family: var(--font-serif);
  font-size: 12px;
  font-style: italic;
  color: var(--ink-4);
  letter-spacing: 0.04em;
}
.nav {
  display: flex;
  gap: 24px;
}
.nav-link {
  font-family: var(--font-sans);
  font-size: 13px;
  font-weight: 600;
  color: var(--ink-3);
  letter-spacing: 0.15em;
  border: none !important;
  padding: 4px 0;
  position: relative;
}
.nav-link:hover {
  color: var(--accent);
  border: none !important;
}
.nav-link.active {
  color: var(--ink-1);
}
.nav-link.active::after {
  content: '';
  position: absolute;
  left: 0; right: 0; bottom: -3px;
  height: 2px;
  background: var(--accent);
}
</style>
