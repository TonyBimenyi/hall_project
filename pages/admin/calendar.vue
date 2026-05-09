<!-- pages/admin/calendar.vue -->
<template>
  <div class="calendar-page">
    <div class="page-header">
      <div>
        <h1>Calendrier des Réservations</h1>
        <p>Vue d'ensemble de l'occupation des salles</p>
      </div>
      <div class="header-actions">
        <div class="calendar-nav">
          <button class="btn-icon" @click="prevMonth"><i class="fas fa-chevron-left"></i></button>
          <h2 class="current-month">{{ currentMonthName }} {{ currentYear }}</h2>
          <button class="btn-icon" @click="nextMonth"><i class="fas fa-chevron-right"></i></button>
        </div>
        <button class="btn btn-primary btn-sm" @click="goToToday">Aujourd'hui</button>
      </div>
    </div>

    <div class="calendar-container card">
      <div class="calendar-grid">
        <!-- Weekdays header -->
        <div v-for="day in weekDays" :key="day" class="weekday-header">
          {{ day }}
        </div>

        <!-- Empty cells for padding -->
        <div v-for="n in firstDayOfMonth" :key="'empty-' + n" class="calendar-day empty"></div>

        <!-- Actual days -->
        <div v-for="day in daysInMonth" :key="day" class="calendar-day" :class="{ 'today': isToday(day) }">
          <div class="day-number">{{ day }}</div>
          <div class="day-events">
            <div 
              v-for="event in getEventsForDay(day)" 
              :key="event.id" 
              class="event-pill"
              :class="event.status"
              @click="viewEvent(event)"
            >
              <span class="event-time">{{ event.hall_name.split(' ')[2] }}</span>
              <span class="event-title">{{ event.customer_name }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="calendar-legend card">
      <div class="legend-item">
        <span class="dot confirmed"></span>
        <span>Confirmé</span>
      </div>
      <div class="legend-item">
        <span class="dot pending"></span>
        <span>En attente</span>
      </div>
      <div class="legend-item">
        <span class="dot paid"></span>
        <span>Payé</span>
      </div>
    </div>

    <!-- View Modal -->
    <AdminAppModal v-model="showViewModal" title="Détails de la réservation" width="400px">
      <div v-if="selectedEvent" class="view-details">
        <div class="detail-item">
          <span class="detail-label">Client</span>
          <span class="detail-val">{{ selectedEvent.customer_name }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">Salle</span>
          <span class="detail-val">{{ selectedEvent.hall_name }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">Événement</span>
          <span class="detail-val">{{ selectedEvent.event_type }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">Période</span>
          <span class="detail-val">Du {{ selectedEvent.start_date }} au {{ selectedEvent.end_date }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">Montant</span>
          <span class="detail-val">{{ selectedEvent.total_price.toLocaleString() }} Fbu</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">Statut</span>
          <span :class="['badge', getBadgeClass(selectedEvent.status)]">
            {{ translateStatus(selectedEvent.status) }}
          </span>
        </div>
      </div>
      <template #footer>
        <button class="btn btn-primary" @click="showViewModal = false">Fermer</button>
      </template>
    </AdminAppModal>
  </div>
</template>

<script setup>
import { api } from '~/composables/useApi'

definePageMeta({ layout: 'admin' })

const weekDays = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim']
const months = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']

const currentDate = ref(new Date())
const showViewModal = ref(false)
const selectedEvent = ref(null)

const events = ref([])

const fetchEvents = async () => {
  try {
    const response = await api.get('bookings/')
    events.value = response.data
  } catch (error) {
    console.error('Error fetching events:', error)
  }
}

onMounted(() => {
  fetchEvents()
})

const currentMonth = computed(() => currentDate.value.getMonth())
const currentYear = computed(() => currentDate.value.getFullYear())
const currentMonthName = computed(() => months[currentMonth.value])

const daysInMonth = computed(() => {
  return new Date(currentYear.value, currentMonth.value + 1, 0).getDate()
})

const firstDayOfMonth = computed(() => {
  const day = new Date(currentYear.value, currentMonth.value, 1).getDay()
  return day === 0 ? 6 : day - 1 // Adjust for Monday start
})

const prevMonth = () => {
  currentDate.value = new Date(currentYear.value, currentMonth.value - 1, 1)
}

const nextMonth = () => {
  currentDate.value = new Date(currentYear.value, currentMonth.value + 1, 1)
}

const goToToday = () => {
  currentDate.value = new Date()
}

const isToday = (day) => {
  const today = new Date()
  return today.getDate() === day && 
         today.getMonth() === currentMonth.value && 
         today.getFullYear() === currentYear.value
}

const getEventsForDay = (day) => {
  const dateStr = `${currentYear.value}-${String(currentMonth.value + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`
  const targetDate = new Date(dateStr)
  
  return events.value.filter(e => {
    const start = new Date(e.start_date)
    const end = new Date(e.end_date)
    return targetDate >= start && targetDate <= end
  })
}

const viewEvent = (event) => {
  selectedEvent.value = event
  showViewModal.value = true
}

const translateStatus = (status) => {
  const map = {
    paid: 'Payé',
    confirmed: 'Confirmé',
    pending: 'En attente',
    cancelled: 'Annulé'
  }
  return map[status] || status
}

const getBadgeClass = (status) => {
  const map = {
    paid: 'badge-success',
    confirmed: 'badge-info',
    pending: 'badge-warning',
    cancelled: 'badge-danger'
  }
  return map[status] || ''
}
</script>

<style scoped>
.calendar-page {
  padding: 0;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-8);
}

.calendar-nav {
  display: flex;
  align-items: center;
  gap: var(--space-6);
}

.current-month {
  font-size: 1.25rem;
  font-weight: 800;
  color: #0f172a;
  min-width: 180px;
  text-align: center;
  margin: 0;
}

.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  overflow: hidden;
  background: #fff;
}

.weekday-header {
  padding: var(--space-4);
  background: #f8fafc;
  text-align: center;
  font-weight: 700;
  font-size: 0.75rem;
  text-transform: uppercase;
  color: #64748b;
  border-bottom: 1px solid #e2e8f0;
}

.calendar-day {
  min-height: 120px;
  padding: var(--space-2);
  border-right: 1px solid #e2e8f0;
  border-bottom: 1px solid #e2e8f0;
  transition: background 0.2s;
}

.calendar-day:nth-child(7n) {
  border-right: none;
}

.calendar-day.empty {
  background: #f1f5f9;
}

.calendar-day.today {
  background: #f0f9ff;
}

.calendar-day.today .day-number {
  background: #0ea5e9;
  color: #fff;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.day-number {
  font-size: 0.875rem;
  font-weight: 600;
  color: #64748b;
  margin-bottom: var(--space-2);
}

.day-events {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.event-pill {
  font-size: 0.7rem;
  padding: 4px 8px;
  border-radius: 4px;
  cursor: pointer;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-weight: 600;
  display: flex;
  gap: 4px;
}

.event-pill.paid { background: #dcfce7; color: #166534; border-left: 3px solid #22c55e; }
.event-pill.confirmed { background: #e0f2fe; color: #075985; border-left: 3px solid #0ea5e9; }
.event-pill.pending { background: #fef3c7; color: #92400e; border-left: 3px solid #f59e0b; }

.event-time {
  opacity: 0.7;
}

.calendar-legend {
  display: flex;
  gap: var(--space-6);
  padding: var(--space-4) var(--space-6);
  margin-top: var(--space-6);
  justify-content: center;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: 0.85rem;
  color: #64748b;
  font-weight: 600;
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.dot.confirmed { background: #0ea5e9; }
.dot.pending { background: #f59e0b; }
.dot.paid { background: #22c55e; }

.view-details .detail-item {
  display: flex;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid #f1f5f9;
}

.view-details .detail-item:last-child {
  border-bottom: none;
}

.view-details .detail-label {
  color: #64748b;
  font-weight: 600;
}

.view-details .detail-val {
  color: #0f172a;
  font-weight: 700;
}
</style>
