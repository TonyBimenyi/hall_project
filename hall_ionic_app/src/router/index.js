import { createRouter, createWebHashHistory } from '@ionic/vue-router'
import { isAuthenticated, setAuthRouter } from '@/lib/api.js'

const routes = [
  {
    path: '/login',
    component: () => import('@/views/Login.vue'),
    meta: { public: true }
  },
  {
    path: '/',
    component: () => import('@/views/Home.vue')
  },
  {
    path: '/bookings',
    component: () => import('@/views/Bookings.vue')
  },
  {
    path: '/bookings/:id',
    component: () => import('@/views/BookingDetail.vue')
  },
  {
    path: '/rooms',
    component: () => import('@/views/Rooms.vue')
  },
  {
    path: '/reports',
    component: () => import('@/views/Reports.vue')
  },
  {
    path: '/compta',
    component: () => import('@/views/Comptabilite.vue')
  },
  {
    path: '/paiements',
    component: () => import('@/views/Paiements.vue')
  },
  {
    path: '/profile',
    component: () => import('@/views/Profile.vue')
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

router.beforeEach((to) => {
  if (to.meta && to.meta.public === true) {
    if (to.path === '/login' && isAuthenticated()) {
      return '/'
    }
    return true
  }
  if (!isAuthenticated()) {
    return { path: '/login', replace: true }
  }
  return true
})

setAuthRouter(router)

export default router
