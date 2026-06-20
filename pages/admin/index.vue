<template>
  <div class="admin-dashboard">
    <section class="hero card">
      <div class="hero-copy">
        <div class="hero-badge">
          <i class="fas fa-gauge-high"></i>
          Tableau de bord
        </div>
        <h1 class="hero-title">Pilotage hôtelier et administratif</h1>
        <p class="hero-subtitle">
          Supervisez la réception, l'occupation des chambres, les encaissements et les alertes clés dans un tableau de bord plus propre et plus moderne.
        </p>

        <div class="hero-actions">
          <button class="btn btn-export btn-sm admin-head-btn" :class="{ 'is-loading': loading }" :disabled="loading" @click="refreshAll">
            <i class="fas fa-rotate-right"></i>
            <span class="btn-label">Actualiser</span>
          </button>
          <NuxtLink to="/admin/bookings" class="btn btn-outline btn-sm admin-head-btn">
            <i class="fas fa-calendar-days"></i>
            <span class="btn-label">Réservations</span>
          </NuxtLink>
          <NuxtLink to="/admin/payments" class="btn btn-primary btn-sm admin-head-btn">
            <i class="fas fa-credit-card"></i>
            <span class="btn-label">Paiements</span>
          </NuxtLink>
          <NuxtLink to="/admin/reports" class="btn btn-secondary btn-sm admin-head-btn">
            <i class="fas fa-chart-line"></i>
            <span class="btn-label">Rapports</span>
          </NuxtLink>
          <NuxtLink to="/admin/calendar" class="btn btn-export btn-sm admin-head-btn">
            <i class="fas fa-calendar-alt"></i>
            <span class="btn-label">Calendrier</span>
          </NuxtLink>
        </div>
      </div>

      <div class="hero-kpis">
        <div class="kpi">
          <div class="kpi-label">Aujourd'hui</div>
          <div class="kpi-value">{{ todayYmd }}</div>
          <div class="kpi-hint">{{ displayBookingsToday }} réservations</div>
        </div>
        <div class="kpi">
          <div class="kpi-label">Arrivées hôtel</div>
          <div class="kpi-value">{{ todayPendingArrivals }}</div>
          <div class="kpi-hint">Clients attendus</div>
        </div>
        <div class="kpi">
          <div class="kpi-label">Séjours en cours</div>
          <div class="kpi-value">{{ inHouseGuestsCount }}</div>
          <div class="kpi-hint">Clients hébergés</div>
        </div>
        <div class="kpi">
          <div class="kpi-label">Encaissement jour</div>
          <div class="kpi-value">{{ formatMoney(revenueTodayAmount) }}</div>
          <div class="kpi-hint">{{ unreadCount }} notification(s)</div>
        </div>
      </div>
    </section>

    <section class="stats-grid">
      <article class="stat-card card">
        <div class="stat-icon primary"><i class="fas fa-calendar-check"></i></div>
        <div class="stat-content">
          <span class="stat-label">Réservations (total)</span>
          <strong class="stat-value">{{ totalBookingsFormatted }}</strong>
          <div class="stat-meta">Toutes périodes</div>
        </div>
      </article>

      <article class="stat-card card">
        <div class="stat-icon info"><i class="fas fa-building"></i></div>
        <div class="stat-content">
          <span class="stat-label">Salles actives</span>
          <strong class="stat-value">{{ activeHallsFormatted }}</strong>
          <div class="stat-meta">Disponibles</div>
        </div>
      </article>

      <article class="stat-card card">
        <div class="stat-icon success"><i class="fas fa-bed"></i></div>
        <div class="stat-content">
          <span class="stat-label">Taux d'occupation chambres</span>
          <strong class="stat-value">{{ roomOccupancyRateLabel }}</strong>
          <div class="stat-meta">{{ occupiedRoomsTodayCount }} occupée(s) / {{ activeRoomsCount }} active(s)</div>
        </div>
      </article>

      <article class="stat-card card">
        <div class="stat-icon primary"><i class="fas fa-right-to-bracket"></i></div>
        <div class="stat-content">
          <span class="stat-label">Check-ins du jour</span>
          <strong class="stat-value">{{ todaysCheckInsFormatted }}</strong>
          <div class="stat-meta">Arrivées enregistrées</div>
        </div>
      </article>

      <article class="stat-card card">
        <div class="stat-icon warning"><i class="fas fa-right-from-bracket"></i></div>
        <div class="stat-content">
          <span class="stat-label">Check-outs du jour</span>
          <strong class="stat-value">{{ todaysCheckOutsFormatted }}</strong>
          <div class="stat-meta">Départs enregistrés</div>
        </div>
      </article>

      <article class="stat-card card">
        <div class="stat-icon warning"><i class="fas fa-hourglass-half"></i></div>
        <div class="stat-content">
          <span class="stat-label">Paiements en attente</span>
          <strong class="stat-value">{{ pendingPaymentsFormatted }}</strong>
          <div class="stat-meta">{{ pendingPaymentsCount > 0 ? 'À solder' : 'Tout est à jour' }}</div>
        </div>
      </article>

      <article class="stat-card card">
        <div class="stat-icon danger"><i class="fas fa-box-open"></i></div>
        <div class="stat-content">
          <span class="stat-label">Stock critique</span>
          <strong class="stat-value">{{ stockAlertsFormatted }}</strong>
          <div class="stat-meta">Rupture ou seuil</div>
        </div>
      </article>

      <article v-if="showFinancialCards" class="stat-card card wide">
        <div class="stat-icon success"><i class="fas fa-wallet"></i></div>
        <div class="stat-content">
          <span class="stat-label">Revenu total</span>
          <strong class="stat-value">{{ formatMoney(totalRevenueAmount) }}</strong>
          <div class="stat-meta">Depuis toujours</div>
        </div>
      </article>

      <article v-if="showFinancialCards" class="stat-card card wide">
        <div class="stat-icon danger"><i class="fas fa-money-bill-wave"></i></div>
        <div class="stat-content">
          <span class="stat-label">Dépenses du mois</span>
          <strong class="stat-value">{{ formatMoney(monthlyExpensesAmount) }}</strong>
          <div class="stat-meta">Mois en cours</div>
        </div>
      </article>
    </section>

    <section class="hotel-overview-grid">
      <article class="focus-card card">
        <div class="focus-head">
          <div>
            <h2>Réception du jour</h2>
            <p>Vue rapide pour l'accueil, les arrivées et les départs.</p>
          </div>
          <NuxtLink to="/admin/rooms" class="btn btn-outline btn-sm admin-head-btn">
            <i class="fas fa-arrow-right"></i>
            <span class="btn-label">Front desk</span>
          </NuxtLink>
        </div>
        <div class="focus-metrics three">
          <div class="focus-metric">
            <span>Arrivées attendues</span>
            <strong>{{ todayPendingArrivals }}</strong>
          </div>
          <div class="focus-metric">
            <span>Check-ins</span>
            <strong>{{ todaysCheckInsFormatted }}</strong>
          </div>
          <div class="focus-metric">
            <span>Check-outs</span>
            <strong>{{ todaysCheckOutsFormatted }}</strong>
          </div>
        </div>
        <div class="focus-list">
          <div class="focus-list-row">
            <span>Séjours en cours</span>
            <strong>{{ inHouseGuestsCount }}</strong>
          </div>
          <div class="focus-list-row">
            <span>Notifications à traiter</span>
            <strong>{{ unreadCount }}</strong>
          </div>
          <div class="focus-list-row">
            <span>Paiements en attente</span>
            <strong>{{ pendingPaymentsFormatted }}</strong>
          </div>
        </div>
      </article>

      <article class="focus-card card accent">
        <div class="focus-head">
          <div>
            <h2>Capacité chambres</h2>
            <p>Disponibilité, occupation et rotation ménage / maintenance.</p>
          </div>
          <span class="focus-badge">{{ roomOccupancyRateLabel }}</span>
        </div>
        <div class="occupancy-progress">
          <div class="occupancy-track">
            <span class="occupancy-fill" :style="{ width: occupancyProgressWidth }"></span>
          </div>
          <div class="occupancy-caption">
            <span>{{ occupiedRoomsTodayCount }} occupée(s)</span>
            <strong>{{ activeRoomsCount }} chambre(s) active(s)</strong>
          </div>
        </div>
        <div class="status-chip-grid">
          <div class="status-chip">
            <span>Disponible</span>
            <strong>{{ roomStatusCounts.available || 0 }}</strong>
          </div>
          <div class="status-chip info">
            <span>Réservée</span>
            <strong>{{ roomStatusCounts.reserved || 0 }}</strong>
          </div>
          <div class="status-chip success">
            <span>Occupée</span>
            <strong>{{ roomStatusCounts.occupied || 0 }}</strong>
          </div>
          <div class="status-chip warning">
            <span>Nettoyage</span>
            <strong>{{ roomStatusCounts.cleaning || 0 }}</strong>
          </div>
          <div class="status-chip danger">
            <span>Maintenance</span>
            <strong>{{ roomStatusCounts.maintenance || 0 }}</strong>
          </div>
        </div>
      </article>

      <article class="focus-card card">
        <div class="focus-head">
          <div>
            <h2>Encaissement & relance</h2>
            <p>Suivi des entrées de caisse et des soldes ouverts.</p>
          </div>
          <NuxtLink to="/admin/payments" class="btn btn-outline btn-sm admin-head-btn">
            <i class="fas fa-credit-card"></i>
            <span class="btn-label">Paiements</span>
          </NuxtLink>
        </div>
        <div class="focus-metrics">
          <div class="focus-metric">
            <span>Aujourd'hui</span>
            <strong>{{ formatMoney(revenueTodayAmount) }}</strong>
          </div>
          <div class="focus-metric">
            <span>7 derniers jours</span>
            <strong>{{ formatMoney(revenueWeekAmount) }}</strong>
          </div>
        </div>
        <div class="focus-list">
          <div class="focus-list-row">
            <span>Reste à encaisser chambres</span>
            <strong>{{ formatMoney(roomBalanceDueAmount) }}</strong>
          </div>
          <div class="focus-list-row">
            <span>Revenu total encaissé</span>
            <strong>{{ formatMoney(totalRevenueAmount) }}</strong>
          </div>
          <div class="focus-list-row">
            <span>Stock critique à suivre</span>
            <strong>{{ stockAlertsFormatted }}</strong>
          </div>
        </div>
      </article>
    </section>

    <section class="dashboard-grid">
      <div class="panel card">
        <div class="panel-head">
          <div>
            <h2>Réservations récentes</h2>
            <p>Dernières entrées enregistrées.</p>
          </div>
          <NuxtLink to="/admin/bookings" class="btn btn-outline btn-sm admin-head-btn">
            <i class="fas fa-arrow-right"></i>
            <span class="btn-label">Voir tout</span>
          </NuxtLink>
        </div>

        <div v-if="loadingBookings" class="panel-loading">
          <div v-for="n in 5" :key="`sk-b-${n}`" class="row-skeleton"></div>
        </div>

        <div v-else-if="recentBookings.length === 0" class="panel-empty">
          <i class="fas fa-inbox"></i>
          <div>
            <strong>Aucune réservation</strong>
            <div class="muted">Aucun enregistrement récent.</div>
          </div>
        </div>

        <div v-else class="rows">
          <div v-for="booking in recentBookings" :key="booking.id" class="row">
            <div class="row-main">
              <div class="row-title">{{ booking.customer_name || '-' }}</div>
              <div class="row-sub">
                <span class="pill">{{ booking.code || '-' }}</span>
                <span class="dot">•</span>
                <span>{{ booking.booking_type === 'room' ? (booking.room_display || '-') : (booking.hall_name || booking.hall?.name || '-') }}</span>
                <span class="dot">•</span>
                <span>{{ booking.start_date }} → {{ booking.end_date }}</span>
              </div>
            </div>
            <div class="row-side">
              <div class="row-value">{{ formatMoney(booking.total_price || 0) }}</div>
              <span class="badge" :class="badgeClass(booking.status)">{{ statusLabel(booking.status) }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="panel card">
        <div class="panel-head">
          <div>
            <h2>Paiements récents</h2>
            <p>Dernières transactions enregistrées.</p>
          </div>
          <NuxtLink to="/admin/payments" class="btn btn-outline btn-sm admin-head-btn">
            <i class="fas fa-arrow-right"></i>
            <span class="btn-label">Voir tout</span>
          </NuxtLink>
        </div>

        <div v-if="loadingPayments" class="panel-loading">
          <div v-for="n in 5" :key="`sk-p-${n}`" class="row-skeleton"></div>
        </div>

        <div v-else-if="recentPayments.length === 0" class="panel-empty">
          <i class="fas fa-inbox"></i>
          <div>
            <strong>Aucun paiement</strong>
            <div class="muted">Aucune transaction récente.</div>
          </div>
        </div>

        <div v-else class="rows">
          <div v-for="payment in recentPayments" :key="payment.id" class="row">
            <div class="row-main">
              <div class="row-title">{{ payment.reference || payment.code || '-' }}</div>
              <div class="row-sub">
                <span class="pill">{{ payment.booking_code || payment.booking?.code || '-' }}</span>
                <span class="dot">•</span>
                <span>{{ payment.method || '-' }}</span>
                <span class="dot">•</span>
                <span>{{ String(payment.date || '').slice(0, 10) || '-' }}</span>
              </div>
            </div>
            <div class="row-side">
              <div class="row-value">{{ formatMoney(payment.amount || 0) }}</div>
              <span class="badge" :class="paymentStatusClass(payment.status)">{{ paymentStatusLabel(payment.status) }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="panel card">
        <div class="panel-head">
          <div>
            <h2>Statut des chambres</h2>
            <p>Disponibilité actuelle, entretien et occupation.</p>
          </div>
          <NuxtLink to="/admin/rooms" class="btn btn-outline btn-sm admin-head-btn">
            <i class="fas fa-bed"></i>
            <span class="btn-label">Gérer</span>
          </NuxtLink>
        </div>

        <div class="alerts room-status-grid">
          <div class="alert-card">
            <div class="alert-icon"><i class="fas fa-circle-check"></i></div>
            <div>
              <div class="alert-title">Disponibles</div>
              <div class="alert-value">{{ roomStatusCounts.available || 0 }}</div>
            </div>
          </div>
          <div class="alert-card info">
            <div class="alert-icon"><i class="fas fa-bookmark"></i></div>
            <div>
              <div class="alert-title">Réservées</div>
              <div class="alert-value">{{ roomStatusCounts.reserved || 0 }}</div>
            </div>
          </div>
          <div class="alert-card">
            <div class="alert-icon"><i class="fas fa-bed"></i></div>
            <div>
              <div class="alert-title">Occupées</div>
              <div class="alert-value">{{ roomStatusCounts.occupied || 0 }}</div>
            </div>
          </div>
          <div class="alert-card warning">
            <div class="alert-icon"><i class="fas fa-soap"></i></div>
            <div>
              <div class="alert-title">Nettoyage</div>
              <div class="alert-value">{{ roomStatusCounts.cleaning || 0 }}</div>
            </div>
          </div>
          <div class="alert-card danger">
            <div class="alert-icon"><i class="fas fa-screwdriver-wrench"></i></div>
            <div>
              <div class="alert-title">Maintenance</div>
              <div class="alert-value">{{ roomStatusCounts.maintenance || 0 }}</div>
            </div>
          </div>
        </div>
      </div>

      <div class="panel card">
        <div class="panel-head">
          <div>
            <h2>Alertes & Stock</h2>
            <p>Ruptures, seuils et actions rapides.</p>
          </div>
          <NuxtLink to="/admin/materials" class="btn btn-outline btn-sm admin-head-btn">
            <i class="fas fa-arrow-right"></i>
            <span class="btn-label">Matériel</span>
          </NuxtLink>
        </div>

        <div class="alerts">
          <div class="alert-card" :class="{ danger: outOfStock.length > 0 }">
            <div class="alert-icon"><i class="fas fa-triangle-exclamation"></i></div>
            <div>
              <div class="alert-title">Rupture</div>
              <div class="alert-value">{{ outOfStock.length }}</div>
            </div>
          </div>
          <div class="alert-card" :class="{ warning: lowStock.length > 0 }">
            <div class="alert-icon"><i class="fas fa-bell"></i></div>
            <div>
              <div class="alert-title">Seuil</div>
              <div class="alert-value">{{ lowStock.length }}</div>
            </div>
          </div>
        </div>

        <div class="mini-list">
          <div v-for="item in stockPreview" :key="`m-${item.id}`" class="mini-row">
            <div class="mini-main">
              <div class="mini-title">{{ item.name }}</div>
              <div class="mini-sub">{{ item.category || '—' }}</div>
            </div>
            <div class="mini-side">
              <span class="mini-pill" :class="Number(item.available_quantity || 0) <= 0 ? 'danger' : 'warning'">
                {{ Number(item.available_quantity || 0) <= 0 ? 'Rupture' : 'Seuil' }}
              </span>
              <strong>{{ Number(item.available_quantity || 0) }}</strong>
            </div>
          </div>

          <div v-if="!stockPreview.length" class="panel-empty compact">
            <i class="fas fa-circle-check"></i>
            <div>
              <strong>Aucune alerte stock</strong>
              <div class="muted">Tout est OK.</div>
            </div>
          </div>
        </div>
      </div>

      <div class="panel card span-2">
        <div class="panel-head">
          <div>
            <h2>Notifications récentes</h2>
            <p>Dernières alertes du système.</p>
          </div>
          <NuxtLink to="/admin/notifications" class="btn btn-outline btn-sm admin-head-btn">
            <i class="fas fa-bell"></i>
            <span class="btn-label">Voir tout</span>
          </NuxtLink>
        </div>

        <div v-if="loadingNotifications" class="panel-loading">
          <div v-for="n in 4" :key="`sk-n-${n}`" class="row-skeleton"></div>
        </div>

        <div v-else-if="recentNotificationsList.length === 0" class="panel-empty compact">
          <i class="fas fa-inbox"></i>
          <div>
            <strong>Aucune notification</strong>
            <div class="muted">Rien à signaler.</div>
          </div>
        </div>

        <div v-else class="rows compact">
          <div v-for="n in recentNotificationsList" :key="n.id" class="row compact">
            <div class="row-main">
              <div class="row-title">{{ n.title }}</div>
              <div class="row-sub">
                <span class="pill">{{ typeLabel(n.type) }}</span>
                <span class="dot">•</span>
                <span>{{ formatTimeAgo(n.timestamp) }}</span>
              </div>
              <div class="row-message">{{ n.message }}</div>
            </div>
            <div class="row-side">
              <span class="badge" :class="n.read ? 'badge-info' : 'badge-warning'">{{ n.read ? 'Lue' : 'Non lue' }}</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
definePageMeta({ layout: 'admin' })

import { api } from '~/composables/useApi'
import { useMoney } from '~/composables/useMoney'
import { canSeeSyntheticRevenue, getStoredUser } from '~/composables/useRoleAccess'
import {
  unreadCount,
  recentNotifications,
  loadingNotifications,
  fetchNotifications,
  formatTimeAgo,
} from '~/composables/useNotifications'

const { formatMoney } = useMoney()

const loading = ref(false)
const loadingSummary = ref(false)
const loadingBookings = ref(false)
const loadingPayments = ref(false)
const loadingMaterials = ref(false)

const summary = ref({
  total_bookings: 0,
  active_halls: 0,
  active_rooms: 0,
  total_revenue: 0,
  monthly_expenses: 0,
  pending_payments: 0,
  material_losses: 0,
  room_occupancy_rate_today: 0,
  occupied_rooms_today: 0,
  todays_check_ins: 0,
  todays_check_outs: 0,
  room_status_counts: {
    available: 0,
    reserved: 0,
    occupied: 0,
    cleaning: 0,
    maintenance: 0,
  },
})

const bookings = ref([])
const payments = ref([])
const materials = ref([])
const currentUser = ref({})

const toYmd = (d) => {
  const dt = (d instanceof Date) ? d : new Date(d)
  if (Number.isNaN(dt.getTime())) return ''
  const y = dt.getFullYear()
  const m = String(dt.getMonth() + 1).padStart(2, '0')
  const day = String(dt.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

const todayYmd = computed(() => toYmd(new Date()))

const showFinancialCards = computed(() => canSeeSyntheticRevenue(currentUser.value))

const totalBookingsCount = computed(() => Number(summary.value.total_bookings || 0))
const activeHallsCount = computed(() => Number(summary.value.active_halls || 0))
const activeRoomsCount = computed(() => Number(summary.value.active_rooms || 0))
const pendingPaymentsCount = computed(() => Number(summary.value.pending_payments || 0))
const totalRevenueAmount = computed(() => Number(summary.value.total_revenue || 0))
const monthlyExpensesAmount = computed(() => Number(summary.value.monthly_expenses || 0))
const occupiedRoomsTodayCount = computed(() => Number(summary.value.occupied_rooms_today || 0))
const todaysCheckInsCount = computed(() => Number(summary.value.todays_check_ins || 0))
const todaysCheckOutsCount = computed(() => Number(summary.value.todays_check_outs || 0))
const roomStatusCounts = computed(() => summary.value.room_status_counts || {})
const roomOccupancyRateLabel = computed(() => `${Number(summary.value.room_occupancy_rate_today || 0).toFixed(1)}%`)

const totalBookingsFormatted = computed(() => totalBookingsCount.value.toLocaleString())
const activeHallsFormatted = computed(() => activeHallsCount.value.toLocaleString())
const pendingPaymentsFormatted = computed(() => pendingPaymentsCount.value.toLocaleString())
const todaysCheckInsFormatted = computed(() => todaysCheckInsCount.value.toLocaleString())
const todaysCheckOutsFormatted = computed(() => todaysCheckOutsCount.value.toLocaleString())

const addDays = (ymd, days) => {
  const base = new Date(`${ymd}T00:00:00`)
  if (Number.isNaN(base.getTime())) return ''
  base.setDate(base.getDate() + days)
  return toYmd(base)
}

const normalizeDate = (value) => String(value || '').slice(0, 10)

const overlapsDate = (start, end, ymd) => {
  const s = normalizeDate(start)
  const e = normalizeDate(end)
  if (!s || !e || !ymd) return false
  return s <= ymd && e >= ymd
}

const displayBookingsToday = computed(() => {
  const t = todayYmd.value
  return (bookings.value || []).filter(b => overlapsDate(b.start_date, b.end_date, t)).length
})

const roomBookings = computed(() => {
  const source = Array.isArray(bookings.value) ? bookings.value : []
  return source.filter((booking) => String(booking.booking_type || '') === 'room' && String(booking.status || '') !== 'cancelled')
})

const todayPendingArrivals = computed(() => {
  const t = todayYmd.value
  return roomBookings.value.filter((booking) => {
    const status = String(booking.status || '')
    return normalizeDate(booking.start_date) === t
      && !booking.checked_in_at
      && ['pending', 'confirmed', 'paid'].includes(status)
  }).length
})

const inHouseGuestsCount = computed(() => {
  return roomBookings.value.filter(booking => booking.checked_in_at && !booking.checked_out_at).length
})

const revenueTodayAmount = computed(() => {
  const t = todayYmd.value
  return (payments.value || []).reduce((sum, payment) => {
    if (String(payment.status || '') !== 'paid') return sum
    return normalizeDate(payment.date || payment.created_at) === t ? sum + Number(payment.amount || 0) : sum
  }, 0)
})

const revenueWeekAmount = computed(() => {
  const end = todayYmd.value
  const start = addDays(end, -6)
  return (payments.value || []).reduce((sum, payment) => {
    if (String(payment.status || '') !== 'paid') return sum
    const ymd = normalizeDate(payment.date || payment.created_at)
    return ymd >= start && ymd <= end ? sum + Number(payment.amount || 0) : sum
  }, 0)
})

const roomBalanceDueAmount = computed(() => {
  return roomBookings.value.reduce((sum, booking) => {
    const remaining = Number(booking.remaining_amount || 0)
    return remaining > 0 ? sum + remaining : sum
  }, 0)
})

const occupancyProgressWidth = computed(() => {
  const rate = Number(summary.value.room_occupancy_rate_today || 0)
  const clamped = Math.min(100, Math.max(0, Number.isFinite(rate) ? rate : 0))
  return `${clamped}%`
})

const recentBookings = computed(() => {
  const source = Array.isArray(bookings.value) ? bookings.value : []
  return source
    .slice()
    .sort((a, b) => {
      const ad = new Date(a.created_at || a.createdAt || 0).getTime()
      const bd = new Date(b.created_at || b.createdAt || 0).getTime()
      if (Number.isFinite(ad) && Number.isFinite(bd) && ad !== bd) return bd - ad
      return Number(b.id || 0) < Number(a.id || 0) ? -1 : 1
    })
    .slice(0, 6)
})

const recentPayments = computed(() => {
  const source = Array.isArray(payments.value) ? payments.value : []
  return source
    .slice()
    .sort((a, b) => {
      const ad = new Date(a.created_at || a.createdAt || a.date || 0).getTime()
      const bd = new Date(b.created_at || b.createdAt || b.date || 0).getTime()
      if (Number.isFinite(ad) && Number.isFinite(bd) && ad !== bd) return bd - ad
      return Number(b.id || 0) < Number(a.id || 0) ? -1 : 1
    })
    .slice(0, 6)
})

const outOfStock = computed(() => {
  return (materials.value || []).filter((m) => Number(m.available_quantity || 0) <= 0)
})

const lowStock = computed(() => {
  return (materials.value || []).filter((m) => {
    const min = Number(m.minimum_quantity || 0)
    if (!min) return false
    const available = Number(m.available_quantity || 0)
    return available > 0 && available <= min
  })
})

const stockPreview = computed(() => {
  const items = [
    ...outOfStock.value.map(m => ({ ...m, __tone: 'danger' })),
    ...lowStock.value.map(m => ({ ...m, __tone: 'warning' })),
  ]
  return items.slice(0, 6)
})

const stockAlertsCount = computed(() => Number(outOfStock.value.length + lowStock.value.length))
const stockAlertsFormatted = computed(() => stockAlertsCount.value.toLocaleString())

const recentNotificationsList = computed(() => {
  const list = Array.isArray(recentNotifications.value) ? recentNotifications.value : []
  return list.slice(0, 6)
})

const badgeClass = (status) => {
  const s = String(status || '')
  if (s === 'paid') return 'badge-success'
  if (s === 'confirmed') return 'badge-info'
  if (s === 'cancelled') return 'badge-danger'
  return 'badge-warning'
}

const statusLabel = (status) => {
  const s = String(status || '')
  if (s === 'paid') return 'Payé'
  if (s === 'confirmed') return 'Confirmé'
  if (s === 'cancelled') return 'Annulé'
  return 'En attente'
}

const paymentStatusClass = (status) => {
  const s = String(status || '')
  if (s === 'paid') return 'badge-success'
  if (s === 'failed') return 'badge-danger'
  return 'badge-warning'
}

const paymentStatusLabel = (status) => {
  const s = String(status || '')
  if (s === 'paid') return 'Payé'
  if (s === 'failed') return 'Échoué'
  return 'En attente'
}

const typeLabel = (type) => {
  const t = String(type || '').toLowerCase()
  if (t === 'success') return 'Succès'
  if (t === 'warning') return 'Alerte'
  if (t === 'danger') return 'Urgent'
  if (t === 'info') return 'Info'
  return 'Notification'
}

const fetchSummary = async () => {
  loadingSummary.value = true
  try {
    const { data } = await api.get('summary/')
    summary.value = data || summary.value
  } catch {
    summary.value = { ...summary.value }
  } finally {
    loadingSummary.value = false
  }
}

const fetchBookings = async () => {
  loadingBookings.value = true
  try {
    const { data } = await api.get('bookings/')
    bookings.value = Array.isArray(data) ? data : []
  } catch {
    bookings.value = []
  } finally {
    loadingBookings.value = false
  }
}

const fetchPayments = async () => {
  loadingPayments.value = true
  try {
    const { data } = await api.get('payments/')
    payments.value = Array.isArray(data) ? data : []
  } catch {
    payments.value = []
  } finally {
    loadingPayments.value = false
  }
}

const fetchMaterials = async () => {
  loadingMaterials.value = true
  try {
    const { data } = await api.get('materials/')
    materials.value = Array.isArray(data) ? data : []
  } catch {
    materials.value = []
  } finally {
    loadingMaterials.value = false
  }
}

const refreshAll = async () => {
  loading.value = true
  currentUser.value = getStoredUser()
  await Promise.allSettled([
    fetchSummary(),
    fetchBookings(),
    fetchPayments(),
    fetchMaterials(),
    fetchNotifications({ force: true }),
  ])
  loading.value = false
}

onMounted(() => {
  refreshAll()
})
</script>

<style scoped>
.admin-dashboard {
  padding: 0;
  display: grid;
  gap: var(--space-8);
}

.hero {
  padding: 0;
  overflow: hidden;
  border: 1px solid var(--gray-200);
  background: linear-gradient(135deg, rgba(15, 23, 42, 0.92), rgba(30, 41, 59, 0.88), rgba(212, 175, 55, 0.28));
  color: #ffffff;
  display: grid;
  grid-template-columns: 1.5fr 0.9fr;
  gap: 0;
}

.hero-copy {
  padding: var(--space-6);
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.18);
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  font-size: 0.72rem;
}

.hero-title {
  margin: var(--space-3) 0 var(--space-2);
  color: #ffffff;
  font-size: 1.55rem;
  font-weight: 900;
  line-height: 1.15;
}

.hero-subtitle {
  color: rgba(255, 255, 255, 0.78);
  max-width: 680px;
  font-weight: 600;
  margin: 0;
}

.hero-actions {
  margin-top: var(--space-4);
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.hero-kpis {
  padding: var(--space-6);
  background: rgba(255, 255, 255, 0.06);
  border-left: 1px solid rgba(255, 255, 255, 0.14);
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  align-content: start;
  gap: 10px;
}

.kpi {
  min-height: 0;
  padding: 12px 14px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.18);
}

.kpi-label {
  font-weight: 900;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  font-size: 0.72rem;
  color: rgba(255, 255, 255, 0.72);
}

.kpi-value {
  margin-top: 8px;
  font-size: 1.12rem;
  font-weight: 900;
  color: #ffffff;
}

.kpi-hint {
  margin-top: 4px;
  color: rgba(255, 255, 255, 0.72);
  font-weight: 700;
  font-size: 0.78rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: var(--space-6);
}

.hotel-overview-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: var(--space-6);
}

.focus-card {
  padding: var(--space-5);
  border-radius: 24px;
  border: 1px solid var(--gray-200);
  background: var(--white);
  box-shadow: 0 18px 40px rgba(15, 23, 42, 0.06);
}

.focus-card.accent {
  background: var(--white);
  border-color: var(--gray-300);
}

.focus-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--space-4);
  margin-bottom: var(--space-5);
}

.focus-head h2 {
  margin: 0;
  font-size: 1.05rem;
  font-weight: 900;
  color: var(--gray-900);
}

.focus-head p {
  margin: 6px 0 0;
  color: var(--gray-500);
  font-size: 0.85rem;
  font-weight: 600;
}

.focus-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 86px;
  padding: 8px 12px;
  border-radius: 999px;
  background: var(--gray-50);
  border: 1px solid var(--gray-200);
  color: var(--gray-900);
  font-weight: 900;
  font-size: 0.9rem;
}

.focus-metrics {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
  margin-bottom: var(--space-4);
}

.focus-metrics.three {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.focus-metric {
  padding: 12px 14px;
  border-radius: 18px;
  border: 1px solid var(--gray-100);
  background: var(--gray-50);
}

.focus-metric span {
  display: block;
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--gray-400);
}

.focus-metric strong {
  display: block;
  margin-top: 8px;
  color: var(--gray-900);
  font-size: 1rem;
  font-weight: 950;
}

.focus-list {
  display: grid;
  gap: 8px;
}

.focus-list-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 11px 13px;
  border-radius: 16px;
  background: var(--gray-50);
  border: 1px solid var(--gray-100);
  color: var(--gray-600);
  font-weight: 700;
}

.focus-list-row strong {
  color: var(--gray-900);
  font-weight: 900;
}

.occupancy-progress {
  display: grid;
  gap: 10px;
  margin-bottom: var(--space-4);
}

.occupancy-track {
  width: 100%;
  height: 12px;
  border-radius: 999px;
  background: var(--gray-100);
  overflow: hidden;
}

.occupancy-fill {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, #22c55e 0%, #0ea5e9 55%, #d4af37 100%);
}

.occupancy-caption {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  color: var(--gray-500);
  font-weight: 700;
  font-size: 0.85rem;
}

.occupancy-caption strong {
  color: var(--gray-900);
}

.status-chip-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.status-chip {
  padding: 12px 14px;
  border-radius: 18px;
  border: 1px solid var(--gray-100);
  background: var(--gray-50);
}

.status-chip span {
  display: block;
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--gray-400);
}

.status-chip strong {
  display: block;
  margin-top: 8px;
  font-size: 1.05rem;
  color: var(--gray-900);
  font-weight: 950;
}

.status-chip.info {
  border-color: rgba(14, 165, 233, 0.22);
}

.status-chip.success {
  border-color: rgba(34, 197, 94, 0.22);
}

.status-chip.warning {
  border-color: rgba(245, 158, 11, 0.24);
}

.status-chip.danger {
  border-color: rgba(239, 68, 68, 0.22);
}

.stat-card {
  padding: var(--space-6);
  display: flex;
  align-items: center;
  gap: var(--space-5);
  border-radius: 22px;
  border: 1px solid var(--gray-200);
  box-shadow: 0 10px 28px rgba(15, 23, 42, 0.06);
  transform: none;
}

.stat-card:hover {
  transform: none;
  box-shadow: 0 14px 34px rgba(15, 23, 42, 0.08);
  background: var(--white);
}

.stat-icon {
  width: 54px;
  height: 54px;
  border-radius: 18px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  border: 1px solid rgba(226, 232, 240, 0.9);
  background: var(--gray-50);
  color: var(--gray-900);
  font-size: 1.15rem;
}

.stat-icon.primary {
  background: rgba(15, 23, 42, 0.08);
  border-color: rgba(15, 23, 42, 0.18);
  color: var(--gray-900);
}

.stat-icon.info {
  background: rgba(14, 165, 233, 0.12);
  border-color: rgba(14, 165, 233, 0.22);
  color: #0284c7;
}

.stat-icon.warning {
  background: rgba(245, 158, 11, 0.14);
  border-color: rgba(245, 158, 11, 0.26);
  color: #b45309;
}

.stat-icon.danger {
  background: rgba(239, 68, 68, 0.12);
  border-color: rgba(239, 68, 68, 0.22);
  color: #dc2626;
}

.stat-icon.success {
  background: rgba(34, 197, 94, 0.12);
  border-color: rgba(34, 197, 94, 0.22);
  color: #16a34a;
}

.stat-content {
  min-width: 0;
  flex: 1;
}

.stat-label {
  display: block;
  font-size: 0.72rem;
  font-weight: 900;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--gray-400);
}

.stat-value {
  display: block;
  margin-top: 10px;
  font-size: 1.55rem;
  font-weight: 950;
  color: var(--gray-900);
  line-height: 1.05;
}

.stat-card.wide {
  grid-column: span 2;
}

.stat-meta {
  margin-top: 6px;
  font-weight: 700;
  font-size: 0.8rem;
  color: var(--gray-400);
}

.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: var(--space-8);
  align-items: start;
}

.panel {
  padding: var(--space-8);
}

.panel-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--space-4);
  margin-bottom: var(--space-6);
  flex-wrap: wrap;
}

.panel-head h2 {
  margin: 0;
  font-size: 1.05rem;
  font-weight: 900;
  color: var(--gray-900);
  font-family: var(--font-sans);
}

.panel-head p {
  margin-top: 6px;
  color: var(--gray-500);
  font-weight: 600;
  font-size: 0.85rem;
}

.panel-loading {
  display: grid;
  gap: 10px;
}

.row-skeleton {
  height: 58px;
  border-radius: 14px;
  background: linear-gradient(90deg, var(--gray-100), var(--gray-200), var(--gray-100));
  background-size: 200% 100%;
  animation: skeleton-move 1.2s ease-in-out infinite;
}

@keyframes skeleton-move {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.panel-empty {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 14px;
  border: 1px dashed var(--gray-200);
  border-radius: 16px;
  color: var(--gray-500);
  font-weight: 700;
}

.panel-empty i {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: var(--gray-100);
  color: var(--gray-400);
}

.panel-empty.compact {
  padding: 12px 14px;
}

.muted {
  color: var(--gray-400);
  font-weight: 600;
  font-size: 0.82rem;
  margin-top: 2px;
}

.rows {
  display: grid;
  gap: 10px;
}

.rows.compact .row {
  padding: 12px 14px;
}

.row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  padding: 14px 16px;
  border-radius: 16px;
  border: 1px solid var(--gray-100);
  background: var(--white);
  transition: var(--transition-fast);
}

.row:hover {
  border-color: rgba(212, 175, 55, 0.45);
  background: var(--gray-50);
}

.row-main {
  min-width: 0;
}

.row-title {
  font-weight: 900;
  color: var(--gray-900);
  font-size: 0.95rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.row-sub {
  margin-top: 6px;
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  color: var(--gray-500);
  font-weight: 700;
  font-size: 0.82rem;
}

.row-message {
  margin-top: 6px;
  color: var(--gray-500);
  font-weight: 600;
  font-size: 0.85rem;
  line-height: 1.45;
}

.pill {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 999px;
  border: 1px solid var(--gray-200);
  background: var(--gray-50);
  color: var(--gray-900);
  font-weight: 900;
  font-size: 0.72rem;
}

.dot {
  opacity: 0.5;
}

.row-side {
  text-align: right;
  display: grid;
  justify-items: end;
  gap: 6px;
  flex-shrink: 0;
}

.row-value {
  font-weight: 900;
  color: var(--gray-900);
}

.alerts {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  margin-bottom: 12px;
}

.room-status-grid {
  margin-bottom: 0;
}

.alert-card {
  display: flex;
  gap: 12px;
  align-items: center;
  padding: 14px 14px;
  border-radius: 16px;
  border: 1px solid var(--gray-100);
  background: var(--white);
}

.alert-card.danger {
  border-color: rgba(239, 68, 68, 0.35);
  background: rgba(239, 68, 68, 0.04);
}

.alert-card.warning {
  border-color: rgba(245, 158, 11, 0.35);
  background: rgba(245, 158, 11, 0.04);
}

.alert-icon {
  width: 42px;
  height: 42px;
  border-radius: 14px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: var(--gray-100);
  color: var(--gray-600);
}

.alert-title {
  font-weight: 900;
  color: var(--gray-900);
  font-size: 0.82rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.alert-value {
  font-weight: 900;
  font-size: 1.2rem;
  color: var(--gray-900);
  margin-top: 4px;
}

.mini-list {
  display: grid;
  gap: 10px;
}

.mini-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  border-radius: 16px;
  border: 1px solid var(--gray-100);
}

.mini-title {
  font-weight: 900;
  color: var(--gray-900);
}

.mini-sub {
  color: var(--gray-400);
  font-weight: 700;
  font-size: 0.8rem;
  margin-top: 4px;
}

.mini-side {
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--gray-900);
}

.mini-pill {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 999px;
  font-weight: 900;
  font-size: 0.72rem;
  border: 1px solid var(--gray-200);
  background: var(--gray-50);
}

.mini-pill.danger {
  border-color: rgba(239, 68, 68, 0.35);
  background: rgba(239, 68, 68, 0.06);
  color: #b91c1c;
}

.mini-pill.warning {
  border-color: rgba(245, 158, 11, 0.35);
  background: rgba(245, 158, 11, 0.06);
  color: #92400e;
}

.span-2 {
  grid-column: span 2;
}

:global(html[data-admin-theme="dark"]) .stat-card,
:global(html[data-admin-theme="dark"]) .focus-card,
:global(html[data-admin-theme="dark"]) .panel,
:global(html[data-admin-theme="dark"]) .row,
:global(html[data-admin-theme="dark"]) .alert-card,
:global(html[data-admin-theme="dark"]) .mini-row {
  background: var(--white);
  border-color: var(--gray-200);
  box-shadow: 0 18px 36px rgba(2, 6, 23, 0.2);
}

:global(html[data-admin-theme="dark"]) .focus-card.accent {
  background: var(--white);
  border-color: var(--gray-300);
}

:global(html[data-admin-theme="dark"]) .stat-label,
:global(html[data-admin-theme="dark"]) .stat-meta,
:global(html[data-admin-theme="dark"]) .panel-head p,
:global(html[data-admin-theme="dark"]) .row-sub,
:global(html[data-admin-theme="dark"]) .row-message,
:global(html[data-admin-theme="dark"]) .muted,
:global(html[data-admin-theme="dark"]) .focus-head p,
:global(html[data-admin-theme="dark"]) .focus-metric span,
:global(html[data-admin-theme="dark"]) .status-chip span,
:global(html[data-admin-theme="dark"]) .focus-list-row,
:global(html[data-admin-theme="dark"]) .occupancy-caption,
:global(html[data-admin-theme="dark"]) .mini-sub {
  color: var(--gray-400);
}

:global(html[data-admin-theme="dark"]) .stat-value,
:global(html[data-admin-theme="dark"]) .panel-head h2,
:global(html[data-admin-theme="dark"]) .row-title,
:global(html[data-admin-theme="dark"]) .row-value,
:global(html[data-admin-theme="dark"]) .alert-title,
:global(html[data-admin-theme="dark"]) .alert-value,
:global(html[data-admin-theme="dark"]) .mini-title,
:global(html[data-admin-theme="dark"]) .mini-side,
:global(html[data-admin-theme="dark"]) .focus-head h2,
:global(html[data-admin-theme="dark"]) .focus-metric strong,
:global(html[data-admin-theme="dark"]) .focus-list-row strong,
:global(html[data-admin-theme="dark"]) .occupancy-caption strong,
:global(html[data-admin-theme="dark"]) .status-chip strong {
  color: var(--gray-700);
}

:global(html[data-admin-theme="dark"]) .stat-icon,
:global(html[data-admin-theme="dark"]) .alert-icon,
:global(html[data-admin-theme="dark"]) .panel-empty i,
:global(html[data-admin-theme="dark"]) .mini-pill,
:global(html[data-admin-theme="dark"]) .focus-badge,
:global(html[data-admin-theme="dark"]) .focus-metric,
:global(html[data-admin-theme="dark"]) .status-chip,
:global(html[data-admin-theme="dark"]) .focus-list-row,
:global(html[data-admin-theme="dark"]) .pill {
  background: var(--gray-50);
  border-color: var(--gray-200);
}

:global(html[data-admin-theme="dark"]) .panel-empty {
  border-color: var(--gray-200);
  background: var(--white);
}

:global(html[data-admin-theme="dark"]) .row:hover {
  background: var(--gray-50);
  border-color: rgba(212, 175, 55, 0.45);
}

@media (max-width: 1100px) {
  .hero {
    grid-template-columns: 1fr;
  }

  .hero-kpis {
    border-left: none;
    border-top: 1px solid rgba(255, 255, 255, 0.14);
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .stats-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .hotel-overview-grid {
    grid-template-columns: 1fr;
  }

  .stat-card.wide {
    grid-column: span 2;
  }

  .dashboard-grid {
    grid-template-columns: 1fr;
  }

  .span-2 {
    grid-column: span 1;
  }
}

@media (max-width: 520px) {
  .hero-copy,
  .hero-kpis {
    padding: var(--space-5);
  }

  .hero-kpis {
    grid-template-columns: 1fr;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .focus-metrics,
  .focus-metrics.three,
  .status-chip-grid {
    grid-template-columns: 1fr;
  }

  .focus-head,
  .occupancy-caption,
  .focus-list-row {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
