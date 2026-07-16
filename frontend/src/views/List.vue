<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { contentsApi, type ContentListItem } from '@/api'
import ContentCard from '@/components/ContentCard.vue'

const route = useRoute()

const list = ref<ContentListItem[]>([])
const total = ref(0)
const loading = ref(true)
const page = ref(1)
const pageSize = 12
const type = ref<string>('')
const sort = ref<string>('newest')
const keyword = ref<string>('')

const load = async () => {
  loading.value = true
  try {
    const res = await contentsApi.list({
      page: page.value,
      page_size: pageSize,
      type: type.value || undefined,
      sort: sort.value,
      keyword: keyword.value || undefined,
    })
    list.value = res.items
    total.value = res.total
  } finally {
    loading.value = false
  }
}

const setType = (t: string) => {
  type.value = type.value === t ? '' : t
  page.value = 1
  load()
}
const setSort = (s: string) => {
  sort.value = s
  load()
}
const setKeyword = (e: Event) => {
  keyword.value = (e.target as HTMLInputElement).value
  page.value = 1
  load()
}

onMounted(() => {
  if (route.query.type) type.value = String(route.query.type)
  if (route.query.sort) sort.value = String(route.query.sort)
  if (route.query.keyword) keyword.value = String(route.query.keyword)
  load()
})

watch(() => route.query, (q) => {
  if (q.type !== undefined) type.value = String(q.type || '')
  if (q.sort !== undefined) sort.value = String(q.sort || 'newest')
  if (q.keyword !== undefined) keyword.value = String(q.keyword || '')
  load()
})

const typeMap: Record<string, string> = { answer: '回答', article: '文章', zvideo: '视频' }
</script>

<template>
  <div class="index-page">
    <div class="container">
      <div class="page-head">
        <div class="kicker">栏目 · 全部内容</div>
        <h1 class="page-title">完整索引</h1>
        <p class="page-meta">
          共收录 <strong>{{ total }}</strong> 条 ·
          按{{ sort === 'hot' ? '热度' : '时间' }}排序
        </p>
      </div>

      <hr class="rule" />

      <div class="tools">
        <div class="tools-row">
          <span class="tools-label">类型</span>
          <button :class="['tool', { active: type === '' }]" @click="setType('')">全部</button>
          <button :class="['tool', { active: type === 'answer' }]" @click="setType('answer')">回答</button>
          <button :class="['tool', { active: type === 'article' }]" @click="setType('article')">文章</button>
          <button :class="['tool', { active: type === 'zvideo' }]" @click="setType('zvideo')">视频</button>
        </div>
        <div class="tools-row">
          <span class="tools-label">排序</span>
          <button :class="['tool', { active: sort === 'newest' }]" @click="setSort('newest')">最新优先</button>
          <button :class="['tool', { active: sort === 'hot' }]" @click="setSort('hot')">热度优先</button>
        </div>
        <div class="tools-row">
          <span class="tools-label">关键词</span>
          <input
            type="search"
            class="search-input"
            placeholder="输入关键词检索标题或摘要…"
            :value="keyword"
            @input="setKeyword"
          />
        </div>
      </div>

      <hr class="rule" />

      <div v-if="loading" class="loading">载入中…</div>
      <div v-else-if="list.length === 0" class="empty">未找到符合条件的内容</div>
      <div v-else class="entries">
        <ContentCard v-for="item in list" :key="item.id" :item="item" :keyword="keyword" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.index-page {
  padding: 32px 0 80px;
}

.page-head {
  padding: 16px 0 24px;
}
.page-title {
  font-family: var(--font-serif);
  font-size: 40px;
  font-weight: 700;
  letter-spacing: 0;
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
  padding: 20px 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.tools-row {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-wrap: wrap;
}
.tools-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--ink-4);
  letter-spacing: 0.1em;
  margin-right: 16px;
  min-width: 56px;
}
.tool {
  font-family: var(--font-sans);
  font-size: 13px;
  font-weight: 500;
  color: var(--ink-3);
  letter-spacing: 0.04em;
  padding: 4px 12px;
  border: 1px solid transparent;
  background: transparent;
  transition: all 0.1s;
}
.tool:hover {
  color: var(--ink-1);
  border-color: var(--rule-soft);
}
.tool.active {
  color: var(--accent);
  border-color: var(--accent);
}
.search-input {
  flex: 1;
  max-width: 360px;
  padding: 7px 12px;
  font-family: var(--font-serif);
  font-size: 14px;
  color: var(--ink-2);
  background: var(--paper-2);
  border: 1px solid var(--rule-soft);
  border-radius: 0;
  outline: none;
  transition: border-color 0.15s;
}
.search-input:focus {
  border-color: var(--ink-1);
  background: var(--paper);
}
.search-input::placeholder {
  color: var(--ink-5);
}

.entries {
  display: flex;
  flex-direction: column;
}
.loading, .empty {
  padding: 80px 0;
  text-align: center;
  font-family: var(--font-serif);
  color: var(--ink-4);
}

@media (max-width: 768px) {
  .page-title { font-size: 28px; }
  .tools-label { min-width: auto; margin-right: 8px; }
}
</style>
