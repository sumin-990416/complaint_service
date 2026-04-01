import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import OfficeDetailView from '../views/OfficeDetailView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: HomeView },
    { path: '/office/:csoSn', name: 'office-detail', component: OfficeDetailView, props: true },
  ],
})

export default router
