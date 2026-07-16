<script setup lang="ts">
import type { ContentListItem } from '@/api'
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import HighlightText from '@/components/HighlightText.vue'

const props = defineProps<{ item: ContentListItem; keyword?: string }>()

const typeLabel = computed(() => {
  const map: Record<string, string> = {
    answer: '回答',
    article: '文章',
    zvideo: '视频',
    video: '视频',
  }
  return map[props.item.type] || props.item.type
})

const dateStr = computed(() => {
  const d = new Date(props.item.created_at)
  return d.toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' })
})
</script>

<template>
  <article class="entry">
    <div class="entry-meta">
      <span class="entry-type">{{ typeLabel }}</span>
      <span class="entry-date">{{ dateStr }}</span>
    </div>
    <h3 class="entry-title">
      <RouterLink :to="`/detail/${item.id}`">
        <HighlightText :text="item.title" :keyword="keyword" />
      </RouterLink>
    </h3>
    <p class="entry-excerpt">
      <HighlightText :text="item.excerpt" :keyword="keyword" />
    </p>
    <div class="entry-foot">
      <span class="entry-author">{{ item.author_name }}</span>
      <span class="entry-stat">赞同 {{ item.voteup_count.toLocaleString() }}</span>
      <span class="entry-stat">评论 {{ item.comment_count }}</span>
      <span v-if="item.has_video" class="entry-flag">含视频</span>
    </div>
  </article>
</template>

<style scoped>
.entry {
  padding: 24px 0;
  border-bottom: 1px solid var(--rule-soft);
  display: flex;
  flex-direction: column;
  gap: 8px;
  background: var(--paper);
}
.entry:last-child {
  border-bottom: 1px solid var(--rule);
}
.entry-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.08em;
}
.entry-type {
  color: var(--accent);
}
.entry-date {
  color: var(--ink-4);
  font-weight: 400;
  letter-spacing: 0.02em;
  font-family: var(--font-serif);
}
.entry-title {
  font-family: var(--font-serif);
  font-size: 22px;
  line-height: 1.3;
  font-weight: 600;
  margin: 4px 0;
}
.entry-title a {
  color: var(--ink-1);
  border: none !important;
}
.entry-title a:hover {
  color: var(--accent);
  border: none !important;
}
.entry-excerpt {
  font-family: var(--font-serif);
  font-size: 15px;
  line-height: 1.6;
  color: var(--ink-3);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.entry-foot {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-top: 4px;
  font-size: 12px;
  color: var(--ink-4);
  letter-spacing: 0.02em;
}
.entry-author {
  color: var(--ink-3);
  font-weight: 500;
}
.entry-stat {
  font-variant-numeric: tabular-nums;
  color: var(--ink-4);
}
.entry-flag {
  margin-left: auto;
  padding: 2px 8px;
  background: var(--ink-1);
  color: var(--paper);
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.08em;
}
</style>
