<template>
  <section class="client-page">
    <div class="container">
      <ReusablePageHeader />

      <div class="gallery-grid">
        <article v-for="(item, i) in images" :key="i" class="card gallery-card">
          <img :src="item.src" :alt="item.alt" />
          <div class="caption">{{ item.alt }}</div>
        </article>
      </div>
    </div>
  </section>
</template>

<script setup>
const { t } = useI18n()

const images = computed(() => [
  { src: 'https://images.unsplash.com/photo-1511795409834-ef04bbd61622?auto=format&fit=crop&w=1200&q=80', alt: t('gallery.items.weddingSetup') },
  { src: 'https://images.unsplash.com/photo-1472653525502-fcd1b145f002?auto=format&fit=crop&w=1200&q=80', alt: t('gallery.items.conferenceHall') },
  { src: 'https://images.unsplash.com/photo-1464366400600-7168b8af9bc3?auto=format&fit=crop&w=1200&q=80', alt: t('gallery.items.eveningDecor') },
  { src: 'https://images.unsplash.com/photo-1519741497674-611481863552?auto=format&fit=crop&w=1200&q=80', alt: t('gallery.items.privateReception') },
  { src: 'https://images.unsplash.com/photo-1519225421980-715cb0215aed?auto=format&fit=crop&w=1200&q=80', alt: t('gallery.items.banquet') },
  { src: 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?auto=format&fit=crop&w=1200&q=80', alt: t('gallery.items.corporateEvent') }
])
</script>

<style scoped>
.client-page {
  background: #f8fafc;
  min-height: 100vh;
  padding: 5rem 0 3rem;
}

.container {
  max-width: 1160px;
  margin: 0 auto;
  padding: 0 1rem;
}

.gallery-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1rem;
}

.gallery-card {
  padding: .55rem;
  border: 1px solid #e2e8f0;
  box-shadow: none;
}

.gallery-card img {
  width: 100%;
  height: 220px;
  object-fit: cover;
  border-radius: 10px;
}

.caption {
  padding: .55rem .2rem .15rem;
  color: #475569;
  font-weight: 600;
  font-size: .92rem;
}
</style>
