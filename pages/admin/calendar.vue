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
        <button class="btn btn-primary btn-sm admin-head-btn" @click="goToToday">
          <i class="fas fa-calendar-day"></i>
          <span class="btn-label">Aujourd'hui</span>
        </button>
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
    <AdminAppModal v-model="showViewModal" title="Détails de la réservation" width="560px">
      <div v-if="selectedEvent" class="entity-view-modal">
        <div class="entity-view-hero">
          <div class="entity-view-avatar">{{ nameInitials(selectedEvent.customer_name) || 'RE' }}</div>
          <div class="entity-view-main">
            <div class="entity-view-code">{{ selectedEvent.code || 'Reservation' }}</div>
            <h3>{{ selectedEvent.customer_name }}</h3>
            <p>{{ selectedEvent.hall_name }} • {{ selectedEvent.event_type }}</p>
          </div>
          <div class="entity-view-badges">
            <span :class="['badge', getBadgeClass(selectedEvent.status)]">{{ translateStatus(selectedEvent.status) }}</span>
            <span class="badge badge-info">{{ formatMoney(selectedEvent.total_price) }}</span>
          </div>
        </div>

        <div class="entity-view-grid">
          <section class="entity-view-card">
            <div class="entity-view-card-title">Réservation</div>
            <div class="entity-view-list">
              <div class="entity-view-item"><span class="entity-view-label">Salle</span><span class="entity-view-value">{{ selectedEvent.hall_name }}</span></div>
              <div class="entity-view-item"><span class="entity-view-label">Événement</span><span class="entity-view-value">{{ selectedEvent.event_type }}</span></div>
              <div class="entity-view-item"><span class="entity-view-label">Période</span><span class="entity-view-value">{{ formatDateRange(selectedEvent.start_date, selectedEvent.end_date) }}</span></div>
            </div>
          </section>

          <section class="entity-view-card">
            <div class="entity-view-card-title">Résumé</div>
            <div class="entity-view-list">
              <div class="entity-view-item"><span class="entity-view-label">Client</span><span class="entity-view-value">{{ selectedEvent.customer_name }}</span></div>
              <div class="entity-view-item"><span class="entity-view-label">Montant</span><span class="entity-view-value">{{ formatMoney(selectedEvent.total_price) }}</span></div>
              <div class="entity-view-item"><span class="entity-view-label">Statut</span><span class="entity-view-value">{{ translateStatus(selectedEvent.status) }}</span></div>
            </div>
          </section>
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
  background: var(--white);
  border: 1px solid var(--gray-200);
  border-radius: 999px;
  padding: 6px 10px;
}

.current-month {
  font-size: 1.05rem;
  font-weight: 800;
  color: var(--gray-900);
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
  border: 1px solid var(--gray-200);
  border-radius: 12px;
  overflow: hidden;
  background: var(--white);
}

.weekday-header {
  padding: var(--space-4);
  background: var(--gray-50);
  text-align: center;
  font-weight: 700;
  font-size: 0.75rem;
  text-transform: uppercase;
  color: var(--gray-500);
  border-bottom: 1px solid var(--gray-200);
}

.calendar-day {
  min-height: 120px;
  padding: var(--space-2);
  border-right: 1px solid var(--gray-200);
  border-bottom: 1px solid var(--gray-200);
  transition: background 0.2s;
}

.calendar-day:nth-child(7n) {
  border-right: none;
}

.calendar-day.empty {
  background: var(--gray-100);
}

.calendar-day.today {
  background: rgba(59, 130, 246, 0.08);
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
  color: var(--gray-500);
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
  background: var(--gray-50);
  border: 1px solid var(--gray-200);
  cursor: default;
}

.event-pill.more {
  background: var(--gray-100);
  color: var(--gray-600);
  border: 1px solid var(--gray-200);
  cursor: default;
  justify-content: center;
  font-weight: 800;
}

.event-pill.paid { background: var(--success-bg); color: var(--success); border-left: 3px solid var(--success); }
.event-pill.confirmed { background: var(--info-bg); color: var(--info); border-left: 3px solid var(--info); }
.event-pill.pending { background: var(--warning-bg); color: var(--warning); border-left: 3px solid var(--warning); }

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
  color: var(--gray-500);
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

.entity-view-modal { display: grid; gap: 18px; }
.entity-view-hero { display: flex; align-items: center; gap: 16px; padding: 18px; border-radius: 20px; background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); color: #ffffff; }
.entity-view-avatar { width: 64px; height: 64px; border-radius: 18px; background: rgba(255,255,255,.14); border: 1px solid rgba(255,255,255,.18); display: flex; align-items: center; justify-content: center; font-size: 1rem; font-weight: 800; letter-spacing: .08em; flex-shrink: 0; }
.entity-view-main { min-width: 0; flex: 1; }
.entity-view-code { display: inline-flex; align-items: center; padding: 6px 10px; border-radius: 999px; background: rgba(255,255,255,.14); font-size: .72rem; font-weight: 800; letter-spacing: .08em; text-transform: uppercase; }
.entity-view-main h3 { margin: 6px 0 4px; font-size: 1.15rem; font-weight: 800; color: #ffffff; }
.entity-view-main p { margin: 0; color: rgba(255,255,255,.78); font-size: .92rem; }
.entity-view-badges { display: flex; flex-direction: column; align-items: flex-end; gap: 8px; }
.entity-view-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; }
.entity-view-card { border: 1px solid var(--gray-200); border-radius: 18px; background: var(--white); padding: 16px; }
.entity-view-card-title { margin-bottom: 14px; font-size: .78rem; font-weight: 800; letter-spacing: .08em; text-transform: uppercase; color: var(--gray-500); }
.entity-view-list { display: grid; gap: 10px; }
.entity-view-item { display: flex; justify-content: space-between; gap: 12px; padding: 10px 12px; border-radius: 14px; background: var(--gray-50); border: 1px solid var(--gray-200); }
.entity-view-label { color: var(--gray-500); font-size: .82rem; font-weight: 700; }
.entity-view-value { color: var(--gray-900); font-size: .9rem; font-weight: 700; text-align: right; word-break: break-word; }

:global(html[data-admin-theme="dark"]) .calendar-nav {
  background: rgba(255, 255, 255, 0.04);
  border-color: rgba(30, 41, 59, 0.95);
}

:global(html[data-admin-theme="dark"]) .calendar-grid {
  background: rgba(15, 23, 42, 0.78);
  border-color: rgba(30, 41, 59, 0.95);
}

:global(html[data-admin-theme="dark"]) .weekday-header {
  background: rgba(255, 255, 255, 0.04);
  border-bottom-color: rgba(30, 41, 59, 0.95);
}

:global(html[data-admin-theme="dark"]) .calendar-day {
  border-right-color: rgba(30, 41, 59, 0.95);
  border-bottom-color: rgba(30, 41, 59, 0.95);
}

:global(html[data-admin-theme="dark"]) .calendar-day.empty {
  background: rgba(255, 255, 255, 0.03);
}

:global(html[data-admin-theme="dark"]) .calendar-day.today {
  background: rgba(59, 130, 246, 0.12);
}

:global(html[data-admin-theme="dark"]) .event-pill.more {
  background: rgba(255, 255, 255, 0.06);
  border-color: rgba(30, 41, 59, 0.95);
}

:global(html[data-admin-theme="dark"]) .event-pill.skeleton {
  background: rgba(255, 255, 255, 0.04);
  border-color: rgba(30, 41, 59, 0.95);
}

:global(html[data-admin-theme="dark"]) .entity-view-card {
  background: rgba(15, 23, 42, 0.78);
  border-color: rgba(30, 41, 59, 0.95);
}

:global(html[data-admin-theme="dark"]) .entity-view-item {
  background: rgba(255, 255, 255, 0.04);
  border-color: rgba(30, 41, 59, 0.95);
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

@media (max-width: 640px) {
  .entity-view-hero { flex-direction: column; align-items: flex-start; }
  .entity-view-badges { align-items: flex-start; flex-direction: row; flex-wrap: wrap; }
  .entity-view-grid { grid-template-columns: 1fr; }
  .entity-view-item { flex-direction: column; }
  .entity-view-value { text-align: left; }
}
</style>
