<script setup lang="ts">
defineProps<{ text: string; keyword?: string }>()

const escapeHtml = (s: string) =>
  s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')

const highlight = (text: string, kw?: string) => {
  if (!kw || !kw.trim()) return escapeHtml(text)
  const safe = escapeHtml(text)
  const safeKw = escapeHtml(kw.trim()).replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  return safe.replace(new RegExp(safeKw, 'gi'), m => `<mark>${m}</mark>`)
}
</script>

<template>
  <span v-html="highlight(text, keyword)"></span>
</template>

<style scoped>
mark {
  background: #fff5b1;
  color: var(--ink-1);
  padding: 0 2px;
  font-weight: 600;
}
</style>
