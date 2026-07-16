<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { authorsApi, type Author, type ContentListItem } from '@/api'

// 实际调用
async function fetchAuthors(sort: string) {
  const r = await fetch(`/api/authors?sort=${sort}&limit=100`).then(r => r.json())
  return r
}

const items = ref<Author[]>([])
const total = ref(0)
const sort = ref<'content' | 'votes'>('content')
const loading = ref(true)

const load = async () => {
  loading.value = true
  try {
    const r = await fetchAuthors(sort.value)
    items.value = r.items
    total.value = r.total
  } finally {
    loading.value = false
  }
}

const setSort = (s: 'content' | 'votes') => {
  sort.value = s
  load()
}

onMounted(load)
</script>

<template>
  <div class="authors-page">
    <div class="container">
      <div class="page-head">
        <div class="kicker">栏目 · 贡献者</div>
        <h1 class="page-title">作者索引</h1>
        <p class="page-meta">
          共 <strong>{{ total }}</strong> 位作者 ·
          按{{ sort === 'votes' ? '总赞同数' : '发布数' }}排序
        </p>
      </div>

      <hr class="rule" />

      <div class="tools">
        <span class="tools-label">排序</span>
        <button :class="['tool', { active: sort === 'content' }]" @click="setSort('content')">按发布数</button>
        <button :class="['tool', { active: sort === 'votes' }]" @click="setSort('votes')">按总赞同</button>
      </div>

      <hr class="rule" />

      <div v-if="loading" class="loading">载入中…</div>
      <div v-else-if="items.length === 0" class="empty">暂无作者</div>
      <div v-else class="author-grid">
        <RouterLink
          v-for="a in items"
          :key="a.id"
          :to="`/author/${encodeURIComponent(a.id)}`"
          class="author-card"
        >
          <div class="author-avatar">
            <img v-if="a.avatar" :src="a.avatar" :alt="a.name" />
            <span v-else class="avatar-fallback">{{ a.name?.[0] || '?' }}</span>
          </div>
          <div class="author-body">
            <h3 class="author-name">{{ a.name }}</h3>
            <p v-if="a.bio" class="author-bio">{{ a.bio }}</p>
            <div class="author-stats">
              <span class="stat"><strong>{{ a.content_count }}</strong> 篇</span>
              <span class="stat"><strong>{{ a.total_votes.toLocaleString() }}</strong> 赞同</span>
            </div>
          </div>
        </RouterLink>
      </div>
    </div>
  </div>
</template>

<style scoped>
.authors-page {
  padding: 32px 0 80px;
}
.page-head {
  padding: 16px 0 24px;
}
.page-title {
  font-family: var(--font-serif);
  font-size: 40px;
  font-weight: 700;
  color: var(--ink-1);
  margin: 8px 0 6px;
}
.page-meta {
  font-family: var(--font-serif);
  font-size: 14px;
  color: var(--ink-4);
}
.page-meta strong {
  color: var(--ink-1);
  font-weight: 700;
  font-variant-numeric: tabular-nums;
}
.tools {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 20px 0;
}
.tools-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--ink-4);
  letter-spacing: 0.1em;
  margin-right: 12px;
}
.tool {
  font-family: var(--font-sans);
  font-size: 13px;
  font-weight: 500;
  color: var(--ink-3);
  padding: 4px 12px;
  border: 1px solid transparent;
  background: transparent;
}
.tool:hover {
  color: var(--ink-1);
  border-color: var(--rule-soft);
}
.tool.active {
  color: var(--accent);
  border-color: var(--accent);
}

.author-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 0;
  border-top: 1px solid var(--rule-soft);
}
.author-card {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 20px;
  border-right: 1px solid var(--rule-soft);
  border-bottom: 1px solid var(--rule-soft);
  background: var(--paper);
  border-top: none !important;
  border-left: none !important;
  text-decoration: none !important;
  transition: background 0.15s;
}
.author-card:hover {
  background: var(--paper-2);
  border-top: none !important;
  border-left: none !important;
  border-right-color: var(--rule-soft) !important;
  border-bottom-color: var(--rule-soft) !important;
}
.author-avatar {
  width: 56px;
  height: 56px;
  flex-shrink: 0;
  border: 1px solid var(--rule-soft);
  overflow: hidden;
  background: var(--paper-2);
  display: flex;
  align-items: center;
  justify-content: center;
}
.author-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.avatar-fallback {
  font-family: var(--font-serif);
  font-size: 24px;
  color: var(--ink-3);
  font-weight: 700;
}
.author-body {
  flex: 1;
  min-width: 0;
}
.author-name {
  font-family: var(--font-serif);
  font-size: 18px;
  font-weight: 700;
  color: var(--ink-1);
  margin: 0 0 4px;
}
.author-bio {
  font-family: var(--font-serif);
  font-size: 13px;
  color: var(--ink-3);
  margin: 0 0 8px;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.author-stats {
  display: flex;
  gap: 12px;
  font-family: var(--font-sans);
  font-size: 12px;
  color: var(--ink-4);
  letter-spacing: 0.02em;
}
.author-stats strong {
  color: var(--ink-1);
  font-weight: 700;
  font-variant-numeric: tabular-nums;
}

.loading, .empty {
  padding: 80px 0;
  text-align: center;
  font-family: var(--font-serif);
  color: var(--ink-4);
}

@media (max-width: 768px) {
  .page-title { font-size: 28px; }
  .author-grid { grid-template-columns: 1fr; }
}
</style>
