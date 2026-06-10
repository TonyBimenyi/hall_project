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
            <template v-if="loadingEvents">
              <div class="event-pill skeleton">
                <span class="skeleton-line skeleton-w-80"></span>
              </div>
            </template>
            <template v-else>
              <div
                v-for="event in visibleEventsForDay(day)"
                :key="event.id"
                class="event-pill"
                :class="event.status"
                @click="viewEvent(event)"
              >
                <span class="event-time">{{ safeHallLabel(event.hall_name) }}</span>
                <span class="event-title">{{ nameInitials(event.customer_name) }}</span>
              </div>
              <div v-if="extraEventsCount(day) > 0" class="event-pill more">
                +{{ extraEventsCount(day) }}
              </div>
            </template>
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
          <span class="detail-val">{{ formatDateRange(selectedEvent.start_date, selectedEvent.end_date) }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">Montant</span>
          <span class="detail-val">{{ formatMoney(selectedEvent.total_price) }}</span>
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
import { useMoney } from '~/composables/useMoney'
import { useDateFormat } from '~/composables/useDateFormat'

const { formatMoney } = useMoney()
const { formatDateRange } = useDateFormat()
import { api } from '~/composables/useApi'

definePageMeta({ layout: 'admin' })

const weekDays = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim']
const months = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']

const currentDate = ref(new Date())
const showViewModal = ref(false)
const selectedEvent = ref(null)

const events = ref([])
const loadingEvents = ref(false)
const isMobile = ref(false)

const fetchEvents = async () => {
  loadingEvents.value = true
  try {
    const response = await api.get('bookings/')
    events.value = response.data
  } catch (error) {
    console.error('Error fetching events:', error)
  } finally {
    loadingEvents.value = false
  }
}

onMounted(() => {
  fetchEvents()
  if (process.client) {
    const update = () => { isMobile.value = window.innerWidth <= 992 }
    update()
    window.addEventListener('resize', update)
    onBeforeUnmount(() => window.removeEventListener('resize', update))
  }
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

const maxEventsPerDay = computed(() => (isMobile.value ? 1 : 3))

const visibleEventsForDay = (day) => {
  const list = getEventsForDay(day)
  return list.slice(0, maxEventsPerDay.value)
}

const extraEventsCount = (day) => {
  const list = getEventsForDay(day)
  return Math.max(0, list.length - maxEventsPerDay.value)
}

const safeHallLabel = (name) => {
  const v = String(name || '').trim()
  if (!v) return ''
  const parts = v.split(/\s+/).filter(Boolean)
  return parts[parts.length - 1] || v
}

const nameInitials = (name) => {
  const value = String(name || '').trim()
  if (!value) return ''
  const words = value.split(/\s+/).filter(Boolean)
  const pick = []
  if (words.length >= 2) {
    pick.push(words[0][0])
    pick.push(words[words.length - 1][0])
  } else {
    const w = words[0] || ''
    pick.push(w[0])
    if (w[1]) pick.push(w[1])
  }
  return pick.filter(Boolean).map(c => String(c).toUpperCase()).join('.')
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
  align-items: flex-start;
  margin-bottom: var(--space-8);
  gap: var(--space-4);
  flex-wrap: wrap;
}

.header-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: var(--space-3);
  flex-wrap: wrap;
}

.calendar-nav {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 999px;
  padding: 6px 10px;
}

.current-month {
  font-size: 1.05rem;
  font-weight: 800;
  color: #0f172a;
  min-width: 160px;
  text-align: center;
  margin: 0;
}

.calendar-container {
  padding: var(--space-5);
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
  border-radius: 8px;
  cursor: pointer;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-weight: 600;
  display: flex;
  gap: 4px;
}

.event-pill.skeleton {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  cursor: default;
}

.event-pill.more {
  background: #f1f5f9;
  color: #334155;
  border: 1px solid #e2e8f0;
  cursor: default;
  justify-content: center;
  font-weight: 800;
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

@media (max-width: 992px) {
  .current-month {
    font-size: 0.95rem;
    min-width: 140px;
  }

  .calendar-container {
    padding: var(--space-4);
  }

  .weekday-header {
    padding: 10px 6px;
    font-size: 0.7rem;
  }

  .calendar-day {
    min-height: 88px;
    padding: 8px;
  }

  .event-pill {
    font-size: 0.68rem;
    padding: 3px 6px;
  }
}
</style>
