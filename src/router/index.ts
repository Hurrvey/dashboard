import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: to => ({ path: '/dashboard', query: to.query }),
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard,
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router

