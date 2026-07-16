<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { contentsApi, type ContentListItem } from '@/api'
import ContentCard from '@/components/ContentCard.vue'

const list = ref<ContentListItem[]>([])
const loading = ref(true)

const router = useRouter()
const searchKeyword = ref('')
const submitSearch = () => {
  const kw = searchKeyword.value.trim()
  router.push({ name: 'list', query: kw ? { keyword: kw } : {} })
}

onMounted(async () => {
  try {
    const res = await contentsApi.list({ sort: 'hot', page_size: 8 })
    list.value = res.items
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="home">
    <div class="container">
      <!-- Hero 居中区域 -->
      <section class="hero">
        <h1 class="paper-title">workbuddy 专题</h1>
        <p class="paper-sub">
          知乎开放平台聚合 · 每日自动同步 · 站内可阅读全部正文与视频记录
        </p>
        <form class="search-form" @submit.prevent="submitSearch">
          <input
            v-model="searchKeyword"
            type="search"
            class="search-input"
            placeholder="搜索知乎 workbuddy 相关内容…"
          />
          <button type="submit" class="search-btn">搜索</button>
        </form>
      </section>

      <hr class="rule" />

      <!-- 热门内容 -->
      <div class="section">
        <div class="section-head">
          <h2 class="section-title">热门内容</h2>
          <RouterLink to="/list?sort=hot" class="more">查看全部 →</RouterLink>
        </div>
        <div v-if="loading" class="loading">载入中…</div>
        <div v-else class="entries">
          <ContentCard v-for="item in list" :key="item.id" :item="item" />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.home {
  padding: 32px 0 80px;
}

/* Hero - 居中 + 放大 */
.hero {
  text-align: center;
  padding: 96px 0 80px;
  max-width: 880px;
  margin: 0 auto;
}
.paper-title {
  font-family: var(--font-serif);
  font-size: 72px;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: var(--ink-1);
  line-height: 1.05;
  margin-bottom: 20px;
}
.paper-sub {
  font-family: var(--font-serif);
  font-size: 18px;
  color: var(--ink-3);
  margin-bottom: 40px;
  line-height: 1.6;
}

/* 搜索框 - 放大 */
.search-form {
  display: flex;
  border: 1px solid var(--ink-1);
  background: var(--paper);
  max-width: 720px;
  margin: 0 auto;
}
.search-input {
  flex: 1;
  padding: 16px 22px;
  font-family: var(--font-serif);
  font-size: 18px;
  color: var(--ink-2);
  background: transparent;
  border: none;
  outline: none;
}
.search-input::placeholder {
  color: var(--ink-5);
}
.search-btn {
  padding: 16px 36px;
  font-family: var(--font-sans);
  font-size: 15px;
  font-weight: 600;
  letter-spacing: 0.15em;
  color: var(--paper);
  background: var(--ink-1);
  border: none;
  cursor: pointer;
}
.search-btn:hover {
  background: var(--accent);
}

/* 章节 */
.section {
  padding: 32px 0;
}
.section-head {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 8px;
}
.section-title {
  font-family: var(--font-serif);
  font-size: 26px;
  font-weight: 700;
  color: var(--ink-1);
}
.more {
  font-family: var(--font-sans);
  font-size: 13px;
  color: var(--ink-3);
  font-weight: 500;
  letter-spacing: 0.05em;
  border: none !important;
}
.more:hover {
  color: var(--accent);
  border: none !important;
}
.entries {
  display: flex;
  flex-direction: column;
  margin-top: 16px;
}
.loading {
  padding: 40px;
  text-align: center;
  color: var(--ink-4);
  font-family: var(--font-serif);
}

@media (max-width: 768px) {
  .hero { padding: 48px 0 40px; }
  .paper-title { font-size: 40px; }
  .paper-sub { font-size: 15px; }
  .search-input { padding: 12px 16px; font-size: 15px; }
  .search-btn { padding: 12px 22px; font-size: 14px; }
}
</style>
