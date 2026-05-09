<template>
  <div class="home-page">
    <section class="hero">
      <div class="hero-bg" :style="{ backgroundImage: `url(${slides[currentSlide].image})` }"></div>
      <div class="hero-overlay"></div>
      <div class="hero-content">
        <h1>{{ slides[currentSlide].title }}</h1>
        <p>
          {{ slides[currentSlide].subtitle }}
        </p>
        <div class="hero-actions">
          <NuxtLink to="/book" class="btn btn-primary">Réserver en ligne</NuxtLink>
          <NuxtLink to="/gallery" class="btn btn-outline">Voir la galerie</NuxtLink>
        </div>
        <div class="hero-dots">
          <button
            v-for="(slide, index) in slides"
            :key="slide.title"
            class="dot"
            :class="{ active: currentSlide === index }"
            @click="setSlide(index)"
          ></button>
        </div>
      </div>
    </section>

    <section class="section clean">
      <div class="section-head">
        <h2>Pourquoi choisir Belta Réception</h2>
        <p>Une expérience fluide, moderne et professionnelle pour tous vos événements.</p>
      </div>
      <div class="feature-grid">
        <article class="feature-card card">
          <i class="fas fa-calendar-check"></i>
          <h3>Réservation rapide</h3>
          <p>Vérifiez les disponibilités et réservez directement en ligne en quelques clics.</p>
        </article>
        <article class="feature-card card">
          <i class="fas fa-building"></i>
          <h3>Salles modulables</h3>
          <p>Plusieurs espaces adaptés à vos besoins, avec capacité et configuration flexibles.</p>
        </article>
        <article class="feature-card card">
          <i class="fas fa-headset"></i>
          <h3>Support dédié</h3>
          <p>Notre équipe vous accompagne avant, pendant et après votre événement.</p>
        </article>
      </div>
    </section>

    <section class="section">
      <div class="section-head">
        <h2>Nos salles disponibles</h2>
        <p>Des espaces pensés pour des expériences mémorables.</p>
      </div>
      <div class="hall-grid">
        <article v-for="hall in halls" :key="hall.id" class="hall-card card">
          <h3>{{ hall.name }}</h3>
          <div class="hall-meta">
            <span><i class="fas fa-users"></i> {{ hall.capacity }} pers.</span>
            <span><i class="fas fa-coins"></i> {{ Number(hall.price_per_day || 0).toLocaleString() }} Fbu / jour</span>
          </div>
          <NuxtLink to="/book" class="btn btn-primary btn-sm">Réserver cette salle</NuxtLink>
        </article>
      </div>
    </section>

    <section class="cta card">
      <h2>Prêt à réserver votre date ?</h2>
      <p>Consultez les disponibilités et soumettez votre demande en ligne.</p>
      <NuxtLink to="/book" class="btn btn-primary">Commencer ma réservation</NuxtLink>
    </section>

    <section class="section">
      <div class="section-head">
        <h2>Nous trouver</h2>
        <p>Cibitoke, Burundi — +25779382580</p>
      </div>
      <div class="map card">
        <iframe
          title="Carte Belta Réception"
          :src="mapSrc"
          loading="lazy"
          referrerpolicy="no-referrer-when-downgrade"
        ></iframe>
      </div>
    </section>
  </div>
</template>

<script setup>
import { api } from '~/composables/useApi'

const halls = ref([])
const currentSlide = ref(0)
let sliderTimer
const slides = [
  {
    title: 'Des événements élégants dans des espaces premium',
    subtitle: 'Belta Réception vous accompagne pour mariages, séminaires et célébrations privées.',
    image: 'https://images.unsplash.com/photo-1519167758481-83f550bb49b3?auto=format&fit=crop&w=1900&q=80'
  },
  {
    title: 'Réservez facilement en ligne',
    subtitle: 'Choisissez votre salle, vos dates et confirmez votre réservation en quelques clics.',
    image: 'https://images.unsplash.com/photo-1472653525502-fcd1b145f002?auto=format&fit=crop&w=1900&q=80'
  },
  {
    title: 'Un accompagnement professionnel du début à la fin',
    subtitle: 'Notre équipe dédiée assure une expérience fluide et un service de qualité.',
    image: 'https://images.unsplash.com/photo-1464366400600-7168b8af9bc3?auto=format&fit=crop&w=1900&q=80'
  }
]

const fetchHalls = async () => {
  try {
    const response = await api.get('halls/')
    halls.value = response.data
  } catch {
    halls.value = []
  }
}

const lat = -2.8778673
const lon = 29.1145199
const mapSrc = computed(() => {
  const bbox = `${lon - 0.02}%2C${lat - 0.02}%2C${lon + 0.02}%2C${lat + 0.02}`
  return `https://www.openstreetmap.org/export/embed.html?bbox=${bbox}&layer=mapnik&marker=${lat}%2C${lon}`
})

const setSlide = (index) => {
  currentSlide.value = index
}

const startSlider = () => {
  sliderTimer = setInterval(() => {
    currentSlide.value = (currentSlide.value + 1) % slides.length
  }, 5000)
}

onMounted(() => {
  fetchHalls()
  startSlider()
})

onBeforeUnmount(() => {
  clearInterval(sliderTimer)
})
</script>

<style scoped>
.home-page {
  background: #f8fafc;
  padding-top: 0;
}

.hero {
  min-height: 100vh;
  position: relative;
  display: flex;
  align-items: center;
  padding-top: 72px;
  box-sizing: border-box;
}

.hero-bg {
  position: absolute;
  inset: 0;
  background-size: cover;
  background-position: center;
  transition: background-image .5s ease-in-out;
}

.hero-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to bottom, rgba(6, 27, 73, 0.82), rgba(6, 27, 73, 0.65));
}

.hero-content {
  position: relative;
  z-index: 1;
  max-width: 860px;
  margin: 0 auto;
  padding: 0 1.5rem;
  text-align: center;
}

.hero-content h1 {
  color: #fff;
  font-size: clamp(2rem, 6vw, 4rem);
  font-weight: 900;
  line-height: 1.1;
  margin-bottom: 1rem;
}

.hero-content p {
  color: rgba(255, 255, 255, 0.92);
  font-size: 1.1rem;
  max-width: 700px;
  margin: 0 auto 2rem;
}

.hero-actions {
  display: flex;
  justify-content: center;
  gap: 0.75rem;
  flex-wrap: wrap;
  margin-bottom: 1.3rem;
}

.hero-dots {
  display: flex;
  justify-content: center;
  gap: .45rem;
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 999px;
  border: 0;
  background: rgba(255, 255, 255, 0.45);
}

.dot.active {
  width: 26px;
  border-radius: 999px;
  background: #d4af37;
}

.section {
  max-width: 1240px;
  margin: 0 auto;
  padding: 4.5rem 1.25rem 0;
}

.section.clean {
  padding-top: 5rem;
}

.section-head {
  text-align: center;
  margin-bottom: 1.5rem;
}

.section-head h2 {
  font-size: 1.8rem;
  font-weight: 800;
  color: #0f172a;
  margin: 0 0 .5rem;
}

.section-head p {
  color: #64748b;
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1rem;
}

.feature-card {
  padding: 1.4rem;
  box-shadow: none;
  border: 1px solid #e2e8f0;
}

.feature-card i {
  width: 42px;
  height: 42px;
  border-radius: 10px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: #eef2ff;
  color: #4338ca;
  margin-bottom: .8rem;
}

.feature-card h3 {
  margin: 0 0 .4rem;
  font-size: 1.05rem;
}

.feature-card p {
  color: #64748b;
  margin: 0;
}

.hall-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.hall-card {
  border: 1px solid #e2e8f0;
  box-shadow: none;
  padding: 1.2rem;
}

.hall-card h3 {
  margin: 0 0 .8rem;
}

.hall-meta {
  display: grid;
  gap: .45rem;
  color: #334155;
  font-size: .92rem;
  margin-bottom: 1rem;
}

.hall-meta span {
  display: inline-flex;
  align-items: center;
  gap: .45rem;
}

.btn-sm {
  width: fit-content;
}

.cta {
  max-width: 1240px;
  margin: 3rem auto 0;
  padding: 2rem 1.25rem;
  text-align: center;
  border: 1px solid #e2e8f0;
  box-shadow: none;
}

.cta h2 {
  margin: 0 0 .4rem;
}

.cta p {
  color: #64748b;
  margin-bottom: 1rem;
}

.map {
  border: 1px solid #e2e8f0;
  box-shadow: none;
  padding: .6rem;
}

.map iframe {
  width: 100%;
  height: 360px;
  border: 0;
  border-radius: 12px;
}
</style>
