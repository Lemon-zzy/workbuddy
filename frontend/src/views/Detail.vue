<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import { contentsApi, type ContentDetail } from '@/api'

const route = useRoute()
const item = ref<ContentDetail | null>(null)
const loading = ref(true)
const notFound = ref(false)

onMounted(async () => {
  try {
    item.value = await contentsApi.detail(String(route.params.id))
  } catch (e) {
    notFound.value = true
  } finally {
    loading.value = false
  }
})

const formatDate = (s: string) => {
  const d = new Date(s)
  return d.toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' })
}

const typeLabel = (t: string) => {
  const m: Record<string, string> = { answer: '回答', article: '文章', zvideo: '视频' }
  return m[t] || t
}
</script>

<template>
  <div class="article-page">
    <div class="container-narrow">
      <RouterLink to="/list" class="back">← 返回索引</RouterLink>

      <div v-if="loading" class="loading">载入中…</div>
      <div v-else-if="notFound" class="empty">未找到该篇目</div>

      <article v-else-if="item" class="article">
        <!-- 文章头 -->
        <div class="article-head">
          <div class="kicker">{{ typeLabel(item.type) }}</div>
          <div class="article-id">编号 {{ item.id }} · 发布于 {{ formatDate(item.created_at) }}</div>
        </div>

        <h1 class="article-title">{{ item.title }}</h1>

        <!-- 作者行 -->
        <div class="byline">
          <span class="by-author">{{ item.author?.name || '知乎贡献者' }}</span>
          <span v-if="item.author?.bio" class="by-meta">· {{ item.author.bio }}</span>
          <a :href="`/api/contents/${item.id}/md`" :download="true" class="by-download" title="下载为 Markdown 文件">
            <span class="by-download-icon">↓</span> 下载 md
          </a>
        </div>

        <!-- 摘要 -->
        <div class="abstract">
          <div class="abstract-label">摘要</div>
          <p>{{ item.excerpt }}</p>
        </div>

        <hr class="rule" />

        <!-- 视频块（如果存在）-->
        <div v-if="item.has_video" class="figure">
          <div class="figure-caption">图 1 · 视频记录（来源：{{ item.source_url }}）</div>
          <div class="video-frame">
            <div class="video-note">
              <div class="kicker">视频</div>
              <p>本篇目含视频记录。点击下方"前往知乎"观看完整视频。</p>
              <a :href="item.source_url" target="_blank" rel="noopener" class="video-link">前往知乎观看 →</a>
            </div>
          </div>
        </div>

        <!-- 正文 -->
        <div class="article-body" v-html="item.content_html"></div>

        <hr class="rule" />

        <!-- 引用信息 -->
        <div class="citation">
          <div class="kicker">引用</div>
          <p class="cite-text">
            <em>{{ item.author_name }}</em>
            <span>({{ formatDate(item.created_at) }}).</span>
            <strong>{{ item.title }}</strong>.
            <em>workbuddy 专题 · 知乎开放平台</em>.
            <span>原文链接：</span>
            <a :href="item.source_url" target="_blank" rel="noopener">{{ item.source_url }}</a>.
            <span>索引时间：{{ formatDate(item.fetched_at) }}。</span>
          </p>
        </div>

        <!-- 关键词 -->
        <div class="keywords" v-if="item.tags?.length">
          <div class="kicker">关键词</div>
          <div class="kw-list">
            <span v-for="t in item.tags" :key="t" class="kw">{{ t }}</span>
          </div>
        </div>

        <hr class="rule" />

        <!-- 指标 -->
        <div class="metrics">
          <div class="metric">
            <div class="metric-figure">{{ item.voteup_count.toLocaleString() }}</div>
            <div class="metric-label">赞同</div>
          </div>
          <div class="metric">
            <div class="metric-figure">{{ item.comment_count.toLocaleString() }}</div>
            <div class="metric-label">评论</div>
          </div>
          <div class="metric">
            <div class="metric-figure">{{ item.has_video ? '有' : '无' }}</div>
            <div class="metric-label">视频</div>
          </div>
        </div>
      </article>
    </div>
  </div>
</template>

<style scoped>
.article-page {
  padding: 32px 0 80px;
}
.back {
  display: inline-block;
  font-size: 12px;
  font-weight: 600;
  color: var(--ink-3);
  letter-spacing: 0.08em;
  margin-bottom: 24px;
  border: none !important;
}
.back:hover { color: var(--accent); border: none !important; }

/* 文章头 */
.article-head {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  padding: 16px 0 12px;
  border-top: 2px solid var(--ink-1);
}
.article-id {
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--ink-4);
  letter-spacing: 0.02em;
}

/* 标题 */
.article-title {
  font-family: var(--font-serif);
  font-size: 36px;
  line-height: 1.3;
  font-weight: 700;
  letter-spacing: 0;
  color: var(--ink-1);
  margin: 16px 0 12px;
}

/* 作者行 */
.byline {
  font-family: var(--font-serif);
  font-size: 15px;
  color: var(--ink-3);
  padding: 8px 0 24px;
  border-bottom: 1px solid var(--rule-soft);
}
.by-author {
  font-weight: 700;
  color: var(--ink-1);
}
.by-download {
  margin-left: 16px;
  font-family: var(--font-sans);
  font-size: 12px;
  font-weight: 600;
  color: var(--accent);
  text-decoration: none;
  padding: 3px 10px;
  border: 1px solid var(--accent);
  letter-spacing: 0.04em;
  transition: background 0.15s, color 0.15s;
}
.by-download:hover {
  background: var(--accent);
  color: white;
}
.by-download-icon { display: inline-block; margin-right: 2px; }

/* 摘要 */
.abstract {
  margin: 24px 0;
  padding: 20px 24px;
  background: var(--paper-2);
  border-left: 3px solid var(--accent);
}
.abstract-label {
  font-family: var(--font-sans);
  font-size: 12px;
  font-weight: 700;
  color: var(--accent);
  letter-spacing: 0.1em;
  margin-bottom: 8px;
}
.abstract p {
  font-family: var(--font-serif);
  font-size: 16px;
  line-height: 1.7;
  color: var(--ink-2);
}

/* 视频 figure */
.figure {
  margin: 32px 0;
}
.figure-caption {
  font-family: var(--font-serif);
  font-size: 13px;
  color: var(--ink-3);
  text-align: center;
  margin-bottom: 8px;
}
.video-frame {
  background: var(--paper-2);
  border: 1px solid var(--rule-soft);
  padding: 48px 24px;
  text-align: center;
}
.video-list { display: flex; flex-direction: column; gap: 24px; }
.video-iframe {
  position: relative;
  width: 100%;
  padding-bottom: 56.25%;
  background: #000;
  border: 1px solid var(--rule-soft);
  overflow: hidden;
}
.video-iframe iframe {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  border: 0;
}
.video-note p {
  font-family: var(--font-serif);
  font-size: 14px;
  color: var(--ink-3);
  margin: 8px 0 16px;
}
.video-link {
  display: inline-block;
  font-family: var(--font-sans);
  font-size: 12px;
  font-weight: 600;
  color: var(--accent);
  letter-spacing: 0.06em;
}

/* 正文 */
.article-body {
  font-family: var(--font-serif);
  font-size: 17px;
  line-height: 1.85;
  color: var(--ink-2);
  margin: 24px 0;
}
.article-body :deep(h2) {
  font-family: var(--font-serif);
  font-size: 22px;
  font-weight: 700;
  color: var(--ink-1);
  margin: 32px 0 12px;
}
.article-body :deep(p) {
  margin-bottom: 18px;
  text-align: justify;
}
.article-body :deep(blockquote) {
  margin: 24px 0;
  padding: 12px 0 12px 20px;
  border-left: 3px solid var(--accent);
  font-style: normal;
  color: var(--ink-3);
  background: var(--paper-2);
}
.article-body :deep(img) {
  margin: 16px auto;
  border: 1px solid var(--rule-soft);
}

/* 引用 */
.citation {
  margin: 24px 0;
  padding: 20px 24px;
  background: var(--paper-2);
}
.cite-text {
  font-family: var(--font-serif);
  font-size: 14px;
  line-height: 1.8;
  color: var(--ink-3);
  margin-top: 8px;
}
.cite-text em { font-style: normal; }
.cite-text strong { color: var(--ink-1); font-weight: 700; }
.cite-text span { color: var(--ink-3); }

/* 关键词 */
.keywords { margin: 24px 0; }
.kw-list {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 8px;
}
.kw {
  font-family: var(--font-serif);
  font-size: 14px;
  color: var(--ink-2);
  padding: 2px 0;
  border-bottom: 1px solid var(--rule-soft);
}

/* 指标 */
.metrics {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 32px;
  padding: 24px 0;
  text-align: center;
}
.metric-figure {
  font-family: var(--font-serif);
  font-size: 28px;
  font-weight: 700;
  color: var(--ink-1);
  font-variant-numeric: tabular-nums;
}
.metric-label {
  font-size: 12px;
  color: var(--ink-4);
  letter-spacing: 0.1em;
  margin-top: 4px;
}

.loading, .empty {
  padding: 80px 0;
  text-align: center;
  font-family: var(--font-serif);
  color: var(--ink-4);
}

@media (max-width: 768px) {
  .article-title { font-size: 26px; }
  .article-head { flex-direction: column; gap: 8px; align-items: flex-start; }
  .metrics { grid-template-columns: repeat(3, 1fr); gap: 16px; }
  .metric-figure { font-size: 22px; }
}
</style>
