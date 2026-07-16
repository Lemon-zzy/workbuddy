<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import ContentCard from '@/components/ContentCard.vue'

interface Work {
  id: string
  title: string
  excerpt: string
  type: string
  voteup_count: number
  comment_count: number
  source_url: string
  created_at: string
  has_video: boolean
}

interface AuthorDetail {
  id: string
  name: string
  avatar?: string
  bio?: string
  badge_text?: string
  follower_count: number
  content_count: number
  total_votes: number
  works: Work[]
}

const route = useRoute()
const author = ref<AuthorDetail | null>(null)
const loading = ref(true)
const notFound = ref(false)

const typeMap: Record<string, string> = { answer: '回答', article: '文章', zvideo: '视频' }

const fetchAuthor = async (id: string) => {
  const r = await fetch(`/api/authors/${encodeURIComponent(id)}`).then(r => {
    if (!r.ok) throw new Error('not found')
    return r.json()
  })
  return r
}

onMounted(async () => {
  try {
    author.value = await fetchAuthor(String(route.params.id))
  } catch {
    notFound.value = true
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="author-page">
    <div class="container">
      <RouterLink to="/authors" class="back">← 返回作者索引</RouterLink>

      <div v-if="loading" class="loading">载入中…</div>
      <div v-else-if="notFound" class="empty">未找到该作者</div>

      <article v-else-if="author" class="author-detail">
        <div class="author-hero">
          <div class="author-avatar-lg">
            <img v-if="author.avatar" :src="author.avatar" :alt="author.name" />
            <span v-else class="avatar-fallback">{{ author.name?.[0] || '?' }}</span>
          </div>
          <div class="author-info">
            <h1 class="author-name">{{ author.name }}</h1>
            <p v-if="author.bio" class="author-bio">{{ author.bio }}</p>
            <div class="author-stats">
              <div class="stat">
                <div class="stat-figure">{{ author.content_count }}</div>
                <div class="stat-label">作品</div>
              </div>
              <div class="stat">
                <div class="stat-figure">{{ author.total_votes.toLocaleString() }}</div>
                <div class="stat-label">总赞同</div>
              </div>
              <div class="stat">
                <div class="stat-figure">{{ author.works.length }}</div>
                <div class="stat-label">已收录</div>
              </div>
            </div>
          </div>
        </div>

        <hr class="rule" />

        <h2 class="works-title">全部作品</h2>
        <div v-if="author.works.length === 0" class="empty">该作者暂无收录作品</div>
        <div v-else class="works">
          <ContentCard
            v-for="w in author.works"
            :key="w.id"
            :item="{
              id: w.id,
              type: w.type,
              title: w.title,
              excerpt: w.excerpt,
              source_url: w.source_url,
              author_name: author.name,
              author_avatar: author.avatar,
              voteup_count: w.voteup_count,
              comment_count: w.comment_count,
              created_at: w.created_at || '',
              has_video: w.has_video,
              tags: [],
            }"
          />
        </div>
      </article>
    </div>
  </div>
</template>

<style scoped>
.author-page { padding: 32px 0 80px; }
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

.author-hero {
  display: flex;
  align-items: flex-start;
  gap: 32px;
  padding: 24px 0 32px;
  border-top: 2px solid var(--ink-1);
}
.author-avatar-lg {
  width: 120px;
  height: 120px;
  flex-shrink: 0;
  border: 1px solid var(--rule-soft);
  overflow: hidden;
  background: var(--paper-2);
  display: flex;
  align-items: center;
  justify-content: center;
}
.author-avatar-lg img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.avatar-fallback {
  font-family: var(--font-serif);
  font-size: 56px;
  color: var(--ink-3);
  font-weight: 700;
}
.author-info {
  flex: 1;
}
.author-name {
  font-family: var(--font-serif);
  font-size: 40px;
  font-weight: 700;
  color: var(--ink-1);
  margin: 0 0 8px;
}
.author-bio {
  font-family: var(--font-serif);
  font-size: 16px;
  color: var(--ink-3);
  line-height: 1.6;
  margin: 0 0 24px;
}
.author-stats {
  display: flex;
  gap: 48px;
  padding: 16px 0 0;
  border-top: 1px solid var(--rule-soft);
}
.stat-figure {
  font-family: var(--font-serif);
  font-size: 28px;
  font-weight: 700;
  color: var(--ink-1);
  font-variant-numeric: tabular-nums;
}
.stat-label {
  font-size: 12px;
  color: var(--ink-4);
  letter-spacing: 0.1em;
  margin-top: 4px;
}

.works-title {
  font-family: var(--font-serif);
  font-size: 24px;
  font-weight: 700;
  color: var(--ink-1);
  margin: 32px 0 16px;
}
.works { display: flex; flex-direction: column; }

.loading, .empty {
  padding: 80px 0;
  text-align: center;
  font-family: var(--font-serif);
  color: var(--ink-4);
}

@media (max-width: 768px) {
  .author-hero { flex-direction: column; gap: 16px; }
  .author-avatar-lg { width: 80px; height: 80px; }
  .avatar-fallback { font-size: 40px; }
  .author-name { font-size: 28px; }
  .author-stats { gap: 24px; }
  .stat-figure { font-size: 22px; }
}
</style>
