import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/Home.vue'),
    },
    {
      path: '/list',
      name: 'list',
      component: () => import('@/views/List.vue'),
    },
    {
      path: '/detail/:id',
      name: 'detail',
      component: () => import('@/views/Detail.vue'),
    },
    {
      path: '/authors',
      name: 'authors',
      component: () => import('@/views/Authors.vue'),
    },
    {
      path: '/author/:id',
      name: 'author-detail',
      component: () => import('@/views/AuthorDetail.vue'),
    },
    {
      path: '/md',
      name: 'md-library',
      component: () => import('@/views/MdLibrary.vue'),
    },
  ],
  scrollBehavior() {
    return { top: 0 }
  },
})

export default router
