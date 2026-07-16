import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 15000,
})

export interface Author {
  id: string
  name: string
  avatar?: string
  bio?: string
  follower_count: number
}

export interface ContentListItem {
  id: string
  type: string
  title: string
  excerpt: string
  cover?: string
  source_url: string
  author_name: string
  author_avatar?: string
  voteup_count: number
  comment_count: number
  created_at: string
  has_video: boolean
  tags: string[]
}

export interface ContentComment {
  author_name: string
  content: string
  voteup_count: number
  created_at?: number | string
}

export interface ContentDetail extends ContentListItem {
  content_html?: string
  fetched_at: string
  author: Author
  // M3 爬虫扩展
  raw_html?: string
  images: string[]
  videos: Array<{ type: string; url: string; title?: string }>
  comments: ContentComment[]
}

export interface ContentListResponse {
  total: number
  page: number
  page_size: number
  items: ContentListItem[]
}

export interface StatsResponse {
  total_contents: number
  total_authors: number
  total_videos: number
  last_sync_at?: string
  type_distribution: Record<string, number>
}

export const contentsApi = {
  list: (params: { page?: number; page_size?: number; type?: string; keyword?: string; sort?: string } = {}) =>
    api.get<ContentListResponse, { data: ContentListResponse }>('/contents', { params }).then(r => r.data),

  detail: (id: string) =>
    api.get<ContentDetail, { data: ContentDetail }>(`/contents/${id}`).then(r => r.data),

  stats: () => api.get<StatsResponse, { data: StatsResponse }>('/contents/_stats/summary').then(r => r.data),

  timeline: (days = 30) => api.get(`/stats/timeline`, { params: { days } }).then(r => r.data),

  tagCloud: () => api.get('/stats/tags').then(r => r.data),
}

export const authorsApi = {
  list: () => api.get('/authors').then(r => r.data),
}

export default api
