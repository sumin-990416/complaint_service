import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import OfficeDetailView from '../views/OfficeDetailView.vue'
import ChatView from '../views/ChatView.vue'
import OnlineView from '../views/OnlineView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: HomeView, meta: { depth: 0, index: 0 } },
    { path: '/online', name: 'online', component: OnlineView, meta: { depth: 0, index: 1 } },
    { path: '/office/:csoSn', name: 'office-detail', component: OfficeDetailView, props: true, meta: { depth: 1 } },
    { path: '/chat', name: 'chat', component: ChatView, meta: { depth: 1 } },
  ],
})

export default router
