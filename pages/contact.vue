<template>
  <section class="client-page">
    <div class="container">
      <ReusablePageHeader />

      <div class="contact-grid">
        <article class="card info-card">
          <h2>{{ t('contact.title') }}</h2>
          <div class="info-line"><i class="fas fa-phone"></i> +257 66 47 66 43 (WhatsApp & Appel)</div>
          <div class="info-line"><i class="fas fa-phone"></i> +257 76 65 39 31 (Appel)</div>
          <div class="info-line"><i class="fas fa-envelope"></i> info@labertha-villa.com</div>
          <div class="info-line"><i class="fas fa-globe"></i> labertha-villa.com</div>
          <div class="info-line"><i class="fas fa-location-dot"></i> Karurama, Cibitoke, Bujumbura, Burundi</div>
          <div class="info-line"><i class="fab fa-facebook"></i> LaBertha Villa</div>
          <div class="info-line"><i class="fab fa-linkedin"></i> LaBertha Villa</div>
          <div class="info-line"><i class="fas fa-clock"></i> {{ t('contact.hours') }}</div>
        </article>

        <article class="card form-card">
          <h2>{{ t('contact.sendMessage') }}</h2>
          <form class="admin-form" @submit.prevent="sendMessage">
            <div class="form-group">
              <label class="form-label">{{ t('contact.name') }}</label>
              <input v-model="form.name" class="form-input" required />
            </div>
            <div class="form-group">
              <label class="form-label">{{ t('contact.email') }}</label>
              <input v-model="form.email" type="email" class="form-input" required />
            </div>
            <div class="form-group">
              <label class="form-label">{{ t('contact.message') }}</label>
              <textarea v-model="form.message" class="form-input" rows="5" required></textarea>
            </div>
            <button class="btn btn-primary">{{ t('contact.send') }}</button>
          </form>
        </article>
      </div>

      <div class="card map-card">
        <h2>{{ t('contact.findUs') }}</h2>
        <div class="map-wrap">
          <iframe
            title="Carte LaBertha Villa"
            :src="mapSrc"
            loading="lazy"
            referrerpolicy="no-referrer-when-downgrade"
          ></iframe>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { notify } from '~/composables/useNotification'

const { t } = useI18n()

const lat = -2.8778673
const lon = 29.1145199
const mapSrc = computed(() => {
  const bbox = `${lon - 0.02}%2C${lat - 0.02}%2C${lon + 0.02}%2C${lat + 0.02}`
  return `https://www.openstreetmap.org/export/embed.html?bbox=${bbox}&layer=mapnik&marker=${lat}%2C${lon}`
})

const form = ref({
  name: '',
  email: '',
  message: ''
})

const sendMessage = () => {
  notify(t('contact.successMessage'), 'success')
  form.value = { name: '', email: '', message: '' }
}
</script>

<style scoped>
.client-page {
  background: #f8fafc;
  min-height: 100vh;
  padding: 5rem 0 3rem;
}

.container {
  max-width: 1240px;
  margin: 0 auto;
  padding: 0 1rem;
}

.contact-grid {
  display: grid;
  grid-template-columns: 1fr 1.2fr;
  gap: 1rem;
}

.info-card, .form-card {
  border: 1px solid #e2e8f0;
  box-shadow: none;
}

.info-card h2, .form-card h2 {
  margin-top: 0;
}

.info-line {
  display: flex;
  align-items: center;
  gap: .55rem;
  margin-bottom: .65rem;
  color: #475569;
}

@media (max-width: 900px) {
  .contact-grid {
    grid-template-columns: 1fr;
  }
}

.map-card {
  margin-top: 1rem;
  border: 1px solid #e2e8f0;
  box-shadow: none;
}

.map-card h2 {
  margin-top: 0;
}

.map-wrap {
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid #e2e8f0;
}

.map-wrap iframe {
  width: 100%;
  height: 360px;
  border: 0;
}
</style>
