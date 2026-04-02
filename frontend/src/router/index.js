import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import OfficeDetailView from '../views/OfficeDetailView.vue'
import ChatView from '../views/ChatView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: HomeView },
    { path: '/office/:csoSn', name: 'office-detail', component: OfficeDetailView, props: true },
    { path: '/chat', name: 'chat', component: ChatView },
  ],
})

export default router
