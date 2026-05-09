<template>
  <section class="client-page">
    <div class="container">
      <ReusablePageHeader />

      <div v-if="!isLoggedIn" class="login-gate card">
        <h2>Connexion requise</h2>
        <p>Connectez-vous pour accéder à votre tableau de bord et voir vos réservations.</p>
        <div class="login-actions">
          <NuxtLink to="/login" class="btn btn-primary btn-sm">Se connecter</NuxtLink>
          <NuxtLink to="/register" class="btn btn-outline btn-sm">Créer un compte</NuxtLink>
        </div>
      </div>

      <template v-else>
      <div class="head-row">
        <div>
          <h2 class="page-title">Bonjour {{ displayName }}</h2>
          <p class="page-subtitle">Suivez vos réservations et vos paiements en un coup d’œil.</p>
        </div>
        <NuxtLink to="/book" class="btn btn-primary">Nouvelle réservation</NuxtLink>
      </div>

      <div class="stats-grid">
        <article class="card stat-card">
          <span class="label">Mes réservations</span>
          <strong>{{ myBookings.length }}</strong>
        </article>
        <article class="card stat-card">
          <span class="label">En attente</span>
          <strong>{{ pendingCount }}</strong>
        </article>
        <article class="card stat-card">
          <span class="label">Confirmées</span>
          <strong>{{ confirmedCount }}</strong>
        </article>
        <article class="card stat-card">
          <span class="label">Montant total</span>
          <strong>{{ totalAmount.toLocaleString() }} Fbu</strong>
        </article>
      </div>

      <div class="card table-card">
        <div class="table-head">
          <h3>Historique de réservation</h3>
          <button class="btn btn-outline btn-sm" @click="fetchBookings">Actualiser</button>
        </div>
        <div class="table-wrap">
          <table class="admin-table">
            <thead>
              <tr>
                <th>Référence</th>
                <th>Événement</th>
                <th>Période</th>
                <th>Montant</th>
                <th>Statut</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="booking in myBookings" :key="booking.id">
                <td>#BR-{{ booking.id }}</td>
                <td>{{ booking.event_type }}</td>
                <td>{{ booking.start_date }} → {{ booking.end_date }}</td>
                <td>{{ Number(booking.total_price || 0).toLocaleString() }} Fbu</td>
                <td>
                  <span class="badge" :class="statusClass(booking.status)">
                    {{ statusText(booking.status) }}
                  </span>
                </td>
              </tr>
              <tr v-if="!loading && myBookings.length === 0">
                <td colspan="5" class="empty">Aucune réservation trouvée.</td>
              </tr>
              <tr v-if="loading">
                <td colspan="5" class="empty">Chargement...</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      </template>
    </div>
  </section>
</template>

<script setup>
import { api } from '~/composables/useApi'
import { notify } from '~/composables/useNotification'

const loading = ref(false)
const bookings = ref([])
const currentUser = ref({})
const isLoggedIn = ref(false)

const displayName = computed(() => {
  const username = currentUser.value?.username
  if (!username) return 'Client'
  return username.charAt(0).toUpperCase() + username.slice(1)
})

const myBookings = computed(() => {
  return bookings.value
})

const pendingCount = computed(() => myBookings.value.filter(b => b.status === 'pending').length)
const confirmedCount = computed(() => myBookings.value.filter(b => b.status === 'confirmed').length)
const totalAmount = computed(() => myBookings.value.reduce((sum, b) => sum + Number(b.total_price || 0), 0))

const statusClass = (status) => {
  if (status === 'confirmed') return 'success'
  if (status === 'cancelled') return 'danger'
  if (status === 'paid') return 'info'
  return 'warning'
}

const statusText = (status) => {
  if (status === 'confirmed') return 'Confirmée'
  if (status === 'cancelled') return 'Annulée'
  if (status === 'paid') return 'Payée'
  return 'En attente'
}

const fetchBookings = async () => {
  if (!isLoggedIn.value) return
  loading.value = true
  try {
    const response = await api.get('bookings/')
    bookings.value = Array.isArray(response.data) ? response.data : []
  } catch {
    notify('Impossible de charger les réservations', 'danger')
    bookings.value = []
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  try {
    currentUser.value = JSON.parse(localStorage.getItem('user') || '{}')
  } catch {
    currentUser.value = {}
  }
  isLoggedIn.value = !!localStorage.getItem('access_token')
  if (isLoggedIn.value) fetchBookings()
})
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

.head-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1rem;
}

.page-title {
  margin: 0;
  font-size: 1.5rem;
  color: #0f172a;
}

.page-subtitle {
  margin-top: .2rem;
  color: #64748b;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
  margin-bottom: 1rem;
}

.stat-card {
  border: 1px solid #e2e8f0;
  box-shadow: none;
}

.stat-card .label {
  color: #64748b;
  font-size: .84rem;
}

.stat-card strong {
  display: block;
  margin-top: .4rem;
  color: #0f172a;
  font-size: 1.35rem;
}

.table-card {
  border: 1px solid #e2e8f0;
  box-shadow: none;
  padding: 1rem;
}

.table-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: .8rem;
}

.table-head h3 {
  margin: 0;
  font-size: 1.1rem;
}

.table-wrap {
  overflow-x: auto;
}

.login-gate {
  border: 1px solid #e2e8f0;
  box-shadow: none;
  padding: 1.2rem;
  margin-bottom: 1rem;
}

.login-gate h2 {
  margin: 0 0 .4rem;
  font-size: 1.1rem;
}

.login-gate p {
  color: #64748b;
  margin: 0 0 .75rem;
}

.login-actions {
  display: flex;
  gap: .6rem;
  flex-wrap: wrap;
}

.empty {
  text-align: center;
  color: #94a3b8;
  padding: 1rem;
}

@media (max-width: 960px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .head-row {
    flex-direction: column;
    align-items: flex-start;
  }
}

@media (max-width: 560px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>
