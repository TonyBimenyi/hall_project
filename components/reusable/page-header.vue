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

const headers = {
  '/about': {
    title: 'À propos',
    subtitle: 'Découvrez LaBertha Villa et notre engagement qualité',
    image: 'https://images.unsplash.com/photo-1478146059778-26028b07395a?auto=format&fit=crop&w=1400&q=80'
  },
  '/services': {
    title: 'Services',
    subtitle: 'Des offres complètes pour vos événements',
    image: 'https://images.unsplash.com/photo-1555244162-803834f70033?auto=format&fit=crop&w=1400&q=80'
  },
  '/gallery': {
    title: 'Galerie',
    subtitle: 'Un aperçu des ambiances que nous créons',
    image: 'https://images.unsplash.com/photo-1464366400600-7168b8af9bc3?auto=format&fit=crop&w=1400&q=80'
  },
  '/contact': {
    title: 'Contact',
    subtitle: 'Parlons de votre projet événementiel',
    image: 'https://images.unsplash.com/photo-1516321497487-e288fb19713f?auto=format&fit=crop&w=1400&q=80'
  },
  '/book': {
    title: 'Réserver',
    subtitle: 'Choisissez vos dates et confirmez en ligne',
    image: 'https://images.unsplash.com/photo-1511578314322-379afb476865?auto=format&fit=crop&w=1400&q=80'
  },
  '/package': {
    title: 'Package',
    subtitle: 'Des formules prêtes pour votre événement',
    image: 'https://images.unsplash.com/photo-1520854221256-17451cc331bf?auto=format&fit=crop&w=1400&q=80'
  },
  '/hotel': {
    title: 'Hotel',
    subtitle: 'Bientot Disponible',
    image: 'https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?auto=format&fit=crop&w=1400&q=80'
  },
  '/dashboard': {
    title: 'Tableau de bord',
    subtitle: 'Gérez vos réservations personnelles',
    image: 'https://images.unsplash.com/photo-1460551885960-7a70d8a4f4be?auto=format&fit=crop&w=1400&q=80'
  }
}

const header = computed(() => headers[route.path] || {
  title: 'LaBertha Villa',
  subtitle: 'Des espaces élégants pour vos événements',
  image: 'https://images.unsplash.com/photo-1519167758481-83f550bb49b3?auto=format&fit=crop&w=1400&q=80'
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
