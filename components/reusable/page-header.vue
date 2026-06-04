<template>
  <section class="page-topbar" :style="{ backgroundImage: `url(${header.image})` }">
    <div class="overlay"></div>
    <div class="content">
      <h1>{{ header.title }}</h1>
      <p>{{ header.subtitle }}</p>
    </div>
  </section>
</template>

<script setup>
import { useRoute } from 'vue-router'

const route = useRoute()
const { t } = useI18n()

const imagesByPath = {
  '/about': {
    image: 'https://images.unsplash.com/photo-1478146059778-26028b07395a?auto=format&fit=crop&w=1400&q=80'
  },
  '/services': {
    image: 'https://images.unsplash.com/photo-1555244162-803834f70033?auto=format&fit=crop&w=1400&q=80'
  },
  '/gallery': {
    image: 'https://images.unsplash.com/photo-1464366400600-7168b8af9bc3?auto=format&fit=crop&w=1400&q=80'
  },
  '/contact': {
    image: 'https://images.unsplash.com/photo-1516321497487-e288fb19713f?auto=format&fit=crop&w=1400&q=80'
  },
  '/book': {
    image: 'https://images.unsplash.com/photo-1511578314322-379afb476865?auto=format&fit=crop&w=1400&q=80'
  },
  '/package': {
    image: 'https://images.unsplash.com/photo-1520854221256-17451cc331bf?auto=format&fit=crop&w=1400&q=80'
  },
  '/hotel': {
    image: 'https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?auto=format&fit=crop&w=1400&q=80'
  },
  '/dashboard': {
    image: 'https://images.unsplash.com/photo-1460551885960-7a70d8a4f4be?auto=format&fit=crop&w=1400&q=80'
  }
}

const normalizedPath = computed(() => {
  let p = route.path || '/'
  p = p.replace(/^\/(fr|en)(\/|$)/, '/')
  if (p.length > 1 && p.endsWith('/')) p = p.slice(0, -1)
  return p
})

const headerKey = computed(() => {
  const p = normalizedPath.value
  if (p === '/' || p === '') return 'default'
  if (p === '/about') return 'about'
  if (p === '/services') return 'services'
  if (p === '/gallery') return 'gallery'
  if (p === '/contact') return 'contact'
  if (p === '/book') return 'book'
  if (p === '/package') return 'package'
  if (p === '/hotel') return 'hotel'
  if (p === '/dashboard') return 'dashboard'
  return 'default'
})

const header = computed(() => {
  const p = normalizedPath.value
  const key = headerKey.value
  const img =
    imagesByPath[p]?.image ||
    'https://images.unsplash.com/photo-1519167758481-83f550bb49b3?auto=format&fit=crop&w=1400&q=80'

  return {
    title: t(`pageHeader.${key}.title`),
    subtitle: t(`pageHeader.${key}.subtitle`),
    image: img
  }
})
</script>

<style scoped>
.page-topbar {
  height: 130px;
  border-radius: 14px;
  overflow: hidden;
  position: relative;
  background-size: cover;
  background-position: center;
  margin-bottom: 1rem;
}

.overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, rgba(15, 23, 42, 0.78), rgba(15, 23, 42, 0.45));
}

.content {
  position: relative;
  z-index: 1;
  height: 100%;
  padding: 1.4rem 1.2rem;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.content h1 {
  margin: 0 0 .3rem;
  color: #fff;
  font-size: 1.5rem;
}

.content p {
  margin: 0;
  color: rgba(255, 255, 255, 0.9);
}
</style>
