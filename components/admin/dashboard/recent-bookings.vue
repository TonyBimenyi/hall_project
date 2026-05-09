<template>
  <div class="recent-bookings">
    <div class="section-header">
      <div class="title-group">
        <h2>Réservations récentes</h2>
        <p>Aperçu des 5 dernières demandes</p>
      </div>
      <NuxtLink to="/admin/bookings" class="btn btn-outline btn-sm">
        Voir tout
      </NuxtLink>
    </div>

    <div class="bookings-list">
      <div
        v-for="booking in bookings"
        :key="booking.id"
        class="booking-item card"
      >
        <div class="booking-main">
          <div class="booking-icon">
            <i :class="getEventIcon(booking.event_type)"></i>
          </div>
          <div class="booking-info">
            <div class="customer-name">{{ booking.customer_name }}</div>
            <div class="event-details">
              {{ booking.event_type }} • {{ booking.start_date }}
            </div>
          </div>
        </div>
        
        <div class="booking-meta">
          <div class="booking-amount">{{ Number(booking.total_price || 0).toLocaleString() }} Fbu</div>
          <span :class="['badge', getBadgeClass(booking.status)]">
            {{ getStatusTranslation(booking.status) }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { api } from '~/composables/useApi'

const bookings = ref([])

const fetchRecentBookings = async () => {
  try {
    const response = await api.get('bookings/')
    // Sort by id descending and take top 5
    bookings.value = response.data.sort((a, b) => b.id - a.id).slice(0, 5)
  } catch (error) {
    console.error('Error fetching recent bookings:', error)
  }
}

onMounted(() => {
  fetchRecentBookings()
})

const getStatusTranslation = (status) => {
  const map = {
    pending: 'En attente',
    confirmed: 'Confirmé',
    paid: 'Payé',
    cancelled: 'Annulé'
  }
  return map[status] || status
}

const getBadgeClass = (status) => {
  const map = {
    pending: 'badge-warning',
    confirmed: 'badge-info',
    paid: 'badge-success',
    cancelled: 'badge-danger'
  }
  return map[status] || ''
}

const getEventIcon = (type) => {
  const map = {
    'Mariage': 'fas fa-heart',
    'Conférence': 'fas fa-microphone',
    'Gala': 'fas fa-star',
    'Anniversaire': 'fas fa-birthday-cake',
    'Réunion': 'fas fa-users'
  }
  return map[type] || 'fas fa-calendar'
}
</script>

<style scoped>
.recent-bookings {
  margin-top: 0;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-6);
}

.title-group h2 {
  font-size: 1.1rem;
  font-weight: 800;
  color: #1e293b;
  margin-bottom: 0;
}

.title-group p {
  color: #94a3b8;
  font-size: 0.8rem;
  font-weight: 600;
}

.btn-sm {
  padding: 0.5rem 1rem;
  font-size: 0.75rem;
  font-weight: 700;
  border-radius: var(--rounded-md);
  border: 1px solid #e2e8f0;
  color: #64748b;
}

.btn-sm:hover {
  background: #f8fafc;
  border-color: var(--primary);
  color: var(--primary);
}

.bookings-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.booking-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-4) var(--space-5);
  border-radius: var(--rounded-xl);
  background: var(--white);
  border: 1px solid #f1f5f9;
  box-shadow: none; /* Cleaner list items */
  transition: var(--transition-fast);
}

.booking-item:hover {
  border-color: var(--accent);
  background: #fdfcf6;
  transform: translateX(4px);
}

.booking-main {
  display: flex;
  align-items: center;
  gap: var(--space-4);
}

.booking-icon {
  width: 40px;
  height: 40px;
  background: #f8fafc;
  color: #64748b;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
}

.customer-name {
  font-weight: 700;
  color: #1e293b;
  font-size: 0.95rem;
}

.event-details {
  font-size: 0.8rem;
  color: #94a3b8;
  font-weight: 500;
}

.booking-meta {
  text-align: right;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: var(--space-1);
}

.booking-amount {
  font-weight: 800;
  color: #0f172a;
  font-size: 0.9rem;
}

.badge {
  font-size: 0.65rem;
  padding: 0.25rem 0.6rem;
}
</style>
