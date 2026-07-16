<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

interface MdItem {
  path: string
  filename: string
  name: string
  size: number
  mtime: string
  year_month: string
}

interface SearchHit {
  path: string
  filename: string
  title: string
  author: string
  year_month: string
  mtime: string
  excerpt: string
  line_hits: { line_no: number; snippet: string; count: number }[]
  total_count: number
}

interface MdFile {
  path: string
  filename: string
  size: number
  mtime: string
  frontmatter: Record<string, string>
  body?: string
  raw?: string
  html?: string
}

const route = useRoute()
const router = useRouter()

const tab = ref<'browse' | 'search'>('browse')

// === 浏览模式 ===
const list = ref<MdItem[]>([])
const total = ref(0)
const loading = ref(true)
const months = ref<string[]>([])
const month = ref<string>('')
const filterKw = ref<string>('')
const selected = ref<MdFile | null>(null)
const loadingFile = ref(false)
const viewMode = ref<'rendered' | 'raw'>('rendered')
const reexporting = ref(false)
const reexportMessage = ref('')
const offset = ref(0)
const limit = 30

// === 搜索模式 ===
const searchKw = ref<string>('')
const searchResults = ref<SearchHit[]>([])
const searchTotal = ref(0)
const searchLoading = ref(false)
const searchError = ref('')
const searchOffset = ref(0)
const searchLimit = 20

const load = async () => {
  loading.value = true
  try {
    const params = new URLSearchParams({ limit: String(limit), offset: String(offset.value) })
    if (month.value) params.set('year_month', month.value)
    if (filterKw.value) params.set('keyword', filterKw.value)
    const r = await fetch(`/api/md/list?${params}`).then(r => r.json())
    list.value = r.items
    total.value = r.total
  } finally {
    loading.value = false
  }
}

const loadMonths = async () => {
  const r = await fetch('/api/md/months').then(r => r.json())
  months.value = r.items
}

const openFile = async (item: MdItem) => {
  loadingFile.value = true
  try {
    const r = await fetch('/api/md/raw/' + encodeURI(item.path) + '?format=both').then(r => r.json())
    selected.value = r
    router.replace({ query: { ...route.query, f: item.path } })
  } finally {
    loadingFile.value = false
  }
}

const closeFile = () => {
  selected.value = null
  const q = { ...route.query }
  delete q.f
  router.replace({ query: q })
}

const setMonth = (m: string) => {
  month.value = month.value === m ? '' : m
  offset.value = 0
  load()
}

const setFilter = (e: Event) => {
  filterKw.value = (e.target as HTMLInputElement).value
  offset.value = 0
  load()
}

// === 搜索 ===
const runSearch = async (resetOffset = true) => {
  if (resetOffset) searchOffset.value = 0
  if (!searchKw.value.trim()) {
    searchResults.value = []
    searchTotal.value = 0
    return
  }
  searchLoading.value = true
  searchError.value = ''
  try {
    const params = new URLSearchParams({
      q: searchKw.value,
      limit: String(searchLimit),
      offset: String(searchOffset.value),
    })
    const r = await fetch('/api/md/search?' + params).then(r => {
      if (!r.ok) throw new Error('HTTP ' + r.status)
      return r.json()
    })
    if (resetOffset) {
      searchResults.value = r.items
    } else {
      searchResults.value = [...searchResults.value, ...r.items]
    }
    searchTotal.value = r.total
  } catch (e: any) {
    searchError.value = String(e)
  } finally {
    searchLoading.value = false
  }
}

const setSearchKw = (e: Event) => {
  searchKw.value = (e.target as HTMLInputElement).value
}

const formatSize = (n: number) => {
  if (n < 1024) return `${n} B`
  if (n < 1024 * 1024) return `${(n / 1024).toFixed(1)} KB`
  return `${(n / 1024 / 1024).toFixed(1)} MB`
}

const formatDate = (s: string) => {
  try {
    return new Date(s).toLocaleString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
  } catch {
    return s
  }
}

const downloadMd = () => {
  if (!selected.value) return
  const blob = new Blob([selected.value.raw || ''], { type: 'text/markdown' })
  const a = document.createElement('a')
  a.href = URL.createObjectURL(blob)
  a.download = selected.value.filename
  a.click()
}

const downloadZip = () => {
  const params = new URLSearchParams()
  if (month.value) params.set('year_month', month.value)
  if (filterKw.value) params.set('keyword', filterKw.value)
  const qs = params.toString()
  window.location.href = '/api/md/download_zip' + (qs ? '?' + qs : '')
}

const reexport = async () => {
  if (reexporting.value) return
  if (!confirm('确认重新导出全部内容到 md 文件？')) return
  reexporting.value = true
  reexportMessage.value = '正在导出...'
  try {
    const r = await fetch('/api/md/reexport', { method: 'POST' }).then(r => r.json())
    if (r.status === 'success') {
      reexportMessage.value = '✅ 重新导出完成'
      await loadMonths()
      await load()
    } else {
      reexportMessage.value = '❌ 导出失败: ' + (r.stderr_tail || r.stdout_tail || '')
    }
  } catch (e) {
    reexportMessage.value = '❌ 错误: ' + e
  } finally {
    setTimeout(() => { reexportMessage.value = '' }, 5000)
    reexporting.value = false
  }
}

const switchTab = (t: 'browse' | 'search') => {
  tab.value = t
  router.replace({ query: { ...route.query, t } })
}

onMounted(async () => {
  await loadMonths()
  const t = String(route.query.t || 'browse')
  tab.value = t === 'search' ? 'search' : 'browse'
  if (route.query.month) month.value = String(route.query.month)
  if (route.query.fk) filterKw.value = String(route.query.fk)
  await load()
  if (route.query.f) {
    const item = list.value.find(i => i.path === route.query.f)
    if (item) await openFile(item)
  }
  if (route.query.sk) {
    searchKw.value = String(route.query.sk)
    await runSearch()
  }
})

watch(() => route.query, async (q) => {
  if (q.t !== undefined) {
    tab.value = q.t === 'search' ? 'search' : 'browse'
  }
  if (q.month !== undefined) {
    month.value = String(q.month || '')
    await load()
  }
  if (q.fk !== undefined) {
    filterKw.value = String(q.fk || '')
    await load()
  }
  if (q.sk !== undefined) {
    searchKw.value = String(q.sk || '')
    if (searchKw.value) await runSearch()
  }
})
</script>

<template>
  <div class="md-page">
    <div class="container">
      <div class="page-head">
        <div class="kicker">栏目 · md 文库</div>
        <h1 class="page-title">Markdown 文件库</h1>
        <p class="page-meta">
          共 <strong>{{ total }}</strong> 篇 · 每篇一个 .md 文件
          <span v-if="month"> · {{ month }}</span>
        </p>
      </div>

      <hr class="rule" />

      <!-- Tab 切换 -->
      <div class="tabs">
        <button :class="['tab', { active: tab === 'browse' }]" @click="switchTab('browse')">浏览</button>
        <button :class="['tab', { active: tab === 'search' }]" @click="switchTab('search')">
          全文搜索
          <span v-if="searchTotal > 0" class="badge">{{ searchTotal }}</span>
        </button>
      </div>

      <!-- 浏览模式 -->
      <div v-if="tab === 'browse'">
        <div class="tools">
          <div class="tools-row">
            <span class="tools-label">月份</span>
            <button :class="['tool', { active: month === '' }]" @click="setMonth('')">全部</button>
            <button
              v-for="m in months"
              :key="m"
              :class="['tool', { active: month === m }]"
              @click="setMonth(m)"
            >{{ m }}</button>
          </div>
          <div class="tools-row">
            <span class="tools-label">搜索</span>
            <input
              type="search"
              class="search-input"
              placeholder="按文件名/标题检索…"
              :value="filterKw"
              @input="setFilter"
            />
          </div>
          <div class="tools-row">
            <span class="tools-label">操作</span>
            <button class="tool" @click="downloadZip">📦 批量下载 (zip)</button>
            <button class="tool" :disabled="reexporting" @click="reexport">
              {{ reexporting ? '导出中…' : '🔄 重新导出 md' }}
            </button>
            <span v-if="reexportMessage" class="reexport-msg">{{ reexportMessage }}</span>
          </div>
        </div>

        <hr class="rule" />

        <div v-if="loading" class="loading">载入中…</div>
        <div v-else-if="list.length === 0" class="empty">无匹配文件</div>
        <div v-else class="file-table">
          <div class="file-row file-head">
            <div class="col-date">时间</div>
            <div class="col-title">文件名</div>
            <div class="col-size">大小</div>
            <div class="col-action">操作</div>
          </div>
          <div
            v-for="f in list"
            :key="f.path"
            class="file-row"
            :class="{ active: selected?.filename === f.filename }"
            @click="openFile(f)"
          >
            <div class="col-date">{{ formatDate(f.mtime) }}</div>
            <div class="col-title">
              <div class="filename">{{ f.filename }}</div>
              <div class="filepath">{{ f.path }}</div>
            </div>
            <div class="col-size">{{ formatSize(f.size) }}</div>
            <div class="col-action">
              <button class="btn-view" @click.stop="openFile(f)">查看</button>
            </div>
          </div>
        </div>
      </div>

      <!-- 搜索模式 -->
      <div v-else>
        <div class="search-bar">
          <input
            type="search"
            class="search-input-lg"
            placeholder="在所有 .md 文件中搜索关键词（标题/正文/作者）"
            :value="searchKw"
            @input="setSearchKw"
            @keydown.enter="runSearch(true)"
            autofocus
          />
          <button class="btn-search" :disabled="searchLoading" @click="runSearch(true)">
            {{ searchLoading ? '搜索中…' : '搜索' }}
          </button>
        </div>

        <div v-if="searchError" class="search-error">⚠ {{ searchError }}</div>

        <div v-if="searchKw && !searchLoading && searchResults.length === 0 && !searchError" class="empty">
          未找到含 "{{ searchKw }}" 的内容
        </div>

        <div v-if="searchLoading" class="loading">搜索中…</div>

        <div v-if="searchResults.length > 0" class="search-results">
          <div class="search-summary">
            共找到 <strong>{{ searchTotal }}</strong> 篇含 "<em>{{ searchKw }}</em>" 的内容
          </div>
          <div
            v-for="r in searchResults"
            :key="r.filename"
            class="search-card"
            @click="openFile({ path: r.path, filename: r.filename, name: r.filename, size: 0, mtime: r.mtime, year_month: r.year_month })"
          >
            <div class="sc-head">
              <div class="sc-title">{{ r.title || r.filename }}</div>
              <div class="sc-meta">
                <span class="sc-author">{{ r.author || '未知' }}</span>
                <span class="sc-date">{{ r.year_month }}</span>
                <span class="sc-count">命中 {{ r.total_count }} 次</span>
              </div>
            </div>
            <div class="sc-hits">
              <div
                v-for="(h, i) in r.line_hits.slice(0, 3)"
                :key="i"
                class="sc-hit"
              >
                <span class="sc-line">L{{ h.line_no }}</span>
                <span class="sc-snippet" v-html="h.snippet"></span>
                <span v-if="h.count > 1" class="sc-hit-count">×{{ h.count }}</span>
              </div>
              <div v-if="r.line_hits.length > 3" class="sc-more">
                还有 {{ r.line_hits.length - 3 }} 处命中…
              </div>
            </div>
          </div>
        </div>

        <div v-if="!searchKw" class="search-tips">
          <div class="tips-title">💡 搜索说明</div>
          <ul>
            <li>搜索所有 .md 文件的<strong>正文</strong>（不只是标题）</li>
            <li>返回每个文件的<strong>命中行号 + 上下文片段</strong>，关键词高亮</li>
            <li>按命中次数排序，<strong>命中越多排越前</strong></li>
            <li>大小写不敏感，中文也支持</li>
          </ul>
        </div>
      </div>
    </div>

    <!-- md 阅读器 -->
    <transition name="slide">
      <div v-if="selected" class="md-reader" @click.self="closeFile">
        <div class="md-reader-inner">
          <div class="md-reader-head">
            <div class="reader-title">{{ selected.frontmatter.title || selected.filename }}</div>
            <div class="reader-actions">
              <div class="view-tabs">
                <button :class="['tab', { active: viewMode === 'rendered' }]" @click="viewMode = 'rendered'">渲染</button>
                <button :class="['tab', { active: viewMode === 'raw' }]" @click="viewMode = 'raw'">源码</button>
              </div>
              <button class="btn" @click="downloadMd">下载 md</button>
              <button class="btn btn-close" @click="closeFile">× 关闭</button>
            </div>
          </div>
          <div class="md-reader-body">
            <div v-if="loadingFile" class="loading">载入中…</div>
            <div v-else>
              <div v-if="selected.frontmatter && Object.keys(selected.frontmatter).length > 0" class="fm-table">
                <table>
                  <tr v-for="(v, k) in selected.frontmatter" :key="k">
                    <th>{{ k }}</th>
                    <td>{{ v }}</td>
                  </tr>
                </table>
              </div>
              <div v-if="viewMode === 'rendered'" class="md-rendered" v-html="selected.html"></div>
              <pre v-else class="md-raw">{{ selected.raw }}</pre>
            </div>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<style scoped>
.md-page { padding: 32px 0 80px; }
.page-head { padding: 16px 0 24px; }
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
.page-meta strong { color: var(--ink-1); font-weight: 700; }

.tabs {
  display: flex;
  gap: 0;
  margin: 20px 0 0;
  border-bottom: 2px solid var(--ink-1);
}
.tabs .tab {
  font-family: var(--font-sans);
  font-size: 14px; font-weight: 600;
  color: var(--ink-3);
  background: transparent;
  border: none;
  padding: 10px 20px;
  cursor: pointer;
  position: relative;
  top: 2px;
  display: flex; align-items: center; gap: 6px;
}
.tabs .tab:hover { color: var(--ink-1); }
.tabs .tab.active {
  color: var(--ink-1);
  background: var(--paper-2);
  border: 2px solid var(--ink-1);
  border-bottom: 2px solid var(--paper-2);
  margin-bottom: -2px;
}
.badge {
  font-family: var(--font-mono);
  font-size: 11px;
  background: var(--accent);
  color: white;
  padding: 1px 6px;
  border-radius: 8px;
  font-weight: 600;
}

.tools { display: flex; flex-direction: column; gap: 12px; padding: 20px 0; }
.tools-row { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.tools-label {
  font-size: 12px; font-weight: 600; color: var(--ink-4);
  letter-spacing: 0.1em; margin-right: 12px; min-width: 48px;
}
.tool {
  font-family: var(--font-sans);
  font-size: 13px; font-weight: 500;
  color: var(--ink-3);
  padding: 4px 12px;
  border: 1px solid transparent;
  background: transparent;
  cursor: pointer;
}
.tool:hover:not(:disabled) { color: var(--ink-1); border-color: var(--rule-soft); }
.tool.active { color: var(--accent); border-color: var(--accent); }
.tool:disabled { opacity: 0.5; cursor: not-allowed; }
.reexport-msg {
  font-family: var(--font-mono);
  font-size: 12px;
  color: var(--ink-3);
  margin-left: 12px;
}

.search-input {
  font-family: var(--font-sans);
  font-size: 14px;
  padding: 6px 12px;
  border: 1px solid var(--rule-soft);
  background: var(--paper);
  color: var(--ink-1);
  min-width: 280px;
}
.search-input:focus { outline: none; border-color: var(--accent); }

.search-bar {
  display: flex;
  gap: 8px;
  padding: 20px 0;
}
.search-input-lg {
  flex: 1;
  font-family: var(--font-sans);
  font-size: 16px;
  padding: 10px 16px;
  border: 1px solid var(--ink-3);
  background: var(--paper);
  color: var(--ink-1);
}
.search-input-lg:focus { outline: none; border-color: var(--accent); }
.btn-search {
  font-family: var(--font-sans);
  font-size: 14px; font-weight: 600;
  background: var(--ink-1);
  color: var(--paper);
  border: none;
  padding: 10px 24px;
  cursor: pointer;
}
.btn-search:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-search:hover:not(:disabled) { background: var(--ink-2); }

.search-error {
  padding: 12px 16px;
  background: #fee;
  color: #c33;
  border: 1px solid #fcc;
  font-family: var(--font-mono);
  font-size: 13px;
  margin: 12px 0;
}

.search-summary {
  font-family: var(--font-serif);
  font-size: 14px;
  color: var(--ink-3);
  padding: 8px 0 16px;
  border-bottom: 1px solid var(--rule-soft);
  margin-bottom: 16px;
}
.search-summary strong { color: var(--ink-1); }
.search-summary em { color: var(--accent); font-style: normal; }

.search-card {
  border: 1px solid var(--rule-soft);
  padding: 16px 20px;
  margin-bottom: 12px;
  cursor: pointer;
  transition: background 0.15s, border-color 0.15s;
}
.search-card:hover { background: var(--paper-2); border-color: var(--ink-3); }

.sc-head { margin-bottom: 12px; }
.sc-title {
  font-family: var(--font-serif);
  font-size: 17px; font-weight: 700;
  color: var(--ink-1);
  margin-bottom: 4px;
}
.sc-meta {
  display: flex; gap: 12px;
  font-family: var(--font-sans);
  font-size: 12px;
  color: var(--ink-4);
}
.sc-author { color: var(--ink-3); }
.sc-count {
  font-family: var(--font-mono);
  background: var(--paper-2);
  padding: 1px 8px;
  color: var(--accent);
  font-weight: 600;
}

.sc-hits { display: flex; flex-direction: column; gap: 6px; }
.sc-hit {
  display: flex;
  gap: 10px;
  font-family: var(--font-serif);
  font-size: 14px;
  line-height: 1.6;
  color: var(--ink-2);
  align-items: baseline;
}
.sc-line {
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--ink-4);
  min-width: 36px;
  text-align: right;
  flex-shrink: 0;
}
.sc-snippet {
  flex: 1;
  word-break: break-word;
}
.sc-snippet :deep(mark) {
  background: #fff3a0;
  color: var(--ink-1);
  padding: 0 2px;
  font-weight: 600;
}
.sc-hit-count {
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--accent);
  font-weight: 600;
  flex-shrink: 0;
}
.sc-more {
  font-family: var(--font-sans);
  font-size: 12px;
  color: var(--ink-4);
  margin-left: 46px;
  font-style: italic;
}

.search-tips {
  padding: 32px 24px;
  background: var(--paper-2);
  border-left: 3px solid var(--ink-3);
  margin: 20px 0;
}
.tips-title {
  font-family: var(--font-sans);
  font-size: 14px;
  font-weight: 700;
  color: var(--ink-2);
  margin-bottom: 12px;
}
.search-tips ul {
  list-style: none;
  padding: 0;
  margin: 0;
}
.search-tips li {
  font-family: var(--font-serif);
  font-size: 14px;
  line-height: 1.8;
  color: var(--ink-3);
  padding: 4px 0 4px 18px;
  position: relative;
}
.search-tips li::before {
  content: "·";
  position: absolute;
  left: 4px;
  color: var(--ink-4);
  font-weight: 700;
}
.search-tips strong { color: var(--ink-1); font-weight: 700; }

.file-table { border-top: 1px solid var(--rule-soft); }
.file-row {
  display: grid;
  grid-template-columns: 160px 1fr 80px 80px;
  gap: 16px;
  padding: 14px 4px;
  border-bottom: 1px solid var(--rule-soft);
  font-size: 13px;
  cursor: pointer;
  transition: background 0.15s;
}
.file-row:hover { background: var(--paper-2); }
.file-row.active { background: var(--paper-2); }
.file-head {
  font-size: 11px; font-weight: 600; color: var(--ink-4);
  letter-spacing: 0.08em; cursor: default; text-transform: uppercase;
}
.file-head:hover { background: transparent; }
.col-date { font-family: var(--font-mono); color: var(--ink-3); font-size: 12px; }
.col-title { min-width: 0; }
.filename {
  font-family: var(--font-mono);
  color: var(--ink-1);
  font-size: 13px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.filepath {
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--ink-4);
  margin-top: 2px;
}
.col-size { color: var(--ink-3); font-family: var(--font-mono); font-size: 12px; text-align: right; }
.col-action { text-align: right; }
.btn-view {
  font-family: var(--font-sans);
  font-size: 12px; color: var(--accent); font-weight: 600;
  background: transparent; border: 1px solid var(--accent);
  padding: 3px 10px; cursor: pointer;
}
.btn-view:hover { background: var(--accent); color: white; }

.loading, .empty { padding: 80px 0; text-align: center; font-family: var(--font-serif); color: var(--ink-4); }

/* 阅读器 */
.md-reader {
  position: fixed; inset: 0;
  background: rgba(0, 0, 0, 0.4);
  z-index: 100;
  display: flex; justify-content: flex-end;
}
.md-reader-inner {
  width: 65%;
  max-width: 900px;
  background: var(--paper);
  height: 100%;
  display: flex; flex-direction: column;
  border-left: 2px solid var(--ink-1);
}
.md-reader-head {
  display: flex; justify-content: space-between; align-items: center;
  padding: 14px 24px;
  border-bottom: 1px solid var(--rule-soft);
  gap: 16px;
}
.reader-title {
  font-family: var(--font-serif);
  font-size: 15px; font-weight: 700;
  color: var(--ink-1);
  flex: 1; min-width: 0;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.reader-actions { display: flex; gap: 8px; align-items: center; flex-shrink: 0; }
.view-tabs { display: flex; border: 1px solid var(--rule-soft); }
.tab2 {
  font-family: var(--font-sans);
  font-size: 12px; font-weight: 600;
  color: var(--ink-3);
  background: transparent;
  border: none;
  padding: 5px 12px;
  cursor: pointer;
}
.tab2.active { background: var(--ink-1); color: var(--paper); }
.tab2:first-child { border-right: 1px solid var(--rule-soft); }
.btn {
  font-family: var(--font-sans);
  font-size: 12px; font-weight: 600;
  color: var(--ink-3);
  background: transparent;
  border: 1px solid var(--rule-soft);
  padding: 4px 12px; cursor: pointer;
}
.btn:hover { color: var(--ink-1); border-color: var(--ink-3); }
.btn-close { color: var(--ink-3); }

.md-reader-body { flex: 1; overflow: auto; padding: 24px 32px; }

.fm-table {
  margin-bottom: 24px;
  border: 1px solid var(--rule-soft);
  font-family: var(--font-mono);
  font-size: 12px;
}
.fm-table table { width: 100%; border-collapse: collapse; }
.fm-table th, .fm-table td {
  padding: 6px 12px;
  border-bottom: 1px solid var(--rule-soft);
  text-align: left;
  vertical-align: top;
}
.fm-table tr:last-child th, .fm-table tr:last-child td { border-bottom: none; }
.fm-table th {
  width: 160px;
  color: var(--ink-4);
  font-weight: 600;
  background: var(--paper-2);
}
.fm-table td {
  color: var(--ink-2);
  word-break: break-all;
}

.md-rendered {
  font-family: var(--font-serif);
  font-size: 16px;
  line-height: 1.8;
  color: var(--ink-2);
}
.md-rendered :deep(h1) { font-size: 32px; font-weight: 700; color: var(--ink-1); margin: 32px 0 16px; border-bottom: 2px solid var(--ink-1); padding-bottom: 8px; }
.md-rendered :deep(h2) { font-size: 22px; font-weight: 700; color: var(--ink-1); margin: 28px 0 12px; font-family: var(--font-serif); }
.md-rendered :deep(h3) { font-size: 18px; font-weight: 700; color: var(--ink-1); margin: 24px 0 8px; }
.md-rendered :deep(p) { margin: 12px 0; text-align: justify; }
.md-rendered :deep(blockquote) { border-left: 3px solid var(--ink-3); padding: 8px 16px; margin: 12px 0; color: var(--ink-3); font-style: italic; background: var(--paper-2); }
.md-rendered :deep(ul), .md-rendered :deep(ol) { margin: 12px 0; padding-left: 24px; }
.md-rendered :deep(li) { margin: 4px 0; }
.md-rendered :deep(a) { color: var(--accent); text-decoration: underline; }
.md-rendered :deep(img) { max-width: 100%; height: auto; display: block; margin: 16px auto; border: 1px solid var(--rule-soft); }
.md-rendered :deep(code) { font-family: var(--font-mono); font-size: 14px; background: var(--paper-2); padding: 1px 5px; border-radius: 2px; }
.md-rendered :deep(pre) { font-family: var(--font-mono); font-size: 13px; background: #1e1e1e; color: #d4d4d4; padding: 16px; border-radius: 4px; overflow: auto; line-height: 1.6; }
.md-rendered :deep(pre code) { background: transparent; color: inherit; padding: 0; }
.md-rendered :deep(hr) { border: none; border-top: 1px solid var(--rule-soft); margin: 24px 0; }
.md-rendered :deep(strong) { font-weight: 700; color: var(--ink-1); }
.md-rendered :deep(em) { font-style: italic; }

.md-raw {
  font-family: var(--font-mono);
  font-size: 12px;
  line-height: 1.7;
  color: var(--ink-2);
  white-space: pre-wrap;
  word-break: break-word;
  background: var(--paper-2);
  padding: 16px;
  border: 1px solid var(--rule-soft);
}

.slide-enter-active, .slide-leave-active { transition: opacity 0.2s; }
.slide-enter-from, .slide-leave-to { opacity: 0; }

@media (max-width: 768px) {
  .page-title { font-size: 28px; }
  .md-reader-inner { width: 100%; max-width: none; }
  .file-row { grid-template-columns: 100px 1fr 70px; }
  .col-action { display: none; }
  .search-bar { flex-direction: column; }
}
</style>
