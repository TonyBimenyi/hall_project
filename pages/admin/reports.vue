<template>
  <div class="admin-reports" :class="{ 'charts-ready': chartsReady }">
    <div class="header-actions">
      <div>
        <h1>Rapports et Statistiques</h1>
        <p class="subtitle">
          Analyse des performances et de l'activité
          <span class="range-pill" v-if="rangeLabel">· {{ rangeLabel }}</span>
        </p>
      </div>
      <div class="filters-group">
        <button class="btn-icon filters-toggle" :class="{ active: filtersOpen }" title="Filtres" @click="filtersOpen = !filtersOpen">
          <i class="fas fa-filter"></i>
        </button>
        <Transition name="filters-fade">
          <div v-show="!isMobile || filtersOpen" class="filters-panel">
            <div class="filters-row">
              <div class="field">
                <span class="field-label">Période</span>
                <select v-model="preset" class="filter-select-clean">
                  <option value="7d">7 jours</option>
                  <option value="28d">28 jours</option>
                  <option value="90d">90 jours</option>
                  <option value="this_month">Ce mois</option>
                  <option value="last_month">Mois dernier</option>
                  <option value="year">Cette année</option>
                  <option value="custom">Personnalisé</option>
                </select>
              </div>

              <div class="field" v-if="preset === 'custom'">
                <span class="field-label">Du</span>
                <input v-model="customStart" class="filter-input-clean" type="date" />
              </div>
              <div class="field" v-if="preset === 'custom'">
                <span class="field-label">Au</span>
                <input v-model="customEnd" class="filter-input-clean" type="date" />
              </div>

              <div class="field">
                <span class="field-label">Paiements</span>
                <select v-model="paymentStatusFilter" class="filter-select-clean">
                  <option value="all">Tous</option>
                  <option value="paid">Payés</option>
                  <option value="pending">En attente</option>
                </select>
              </div>

              <div class="field">
                <span class="field-label">Réservations</span>
                <select v-model="bookingStatusFilter" class="filter-select-clean">
                  <option value="all">Toutes</option>
                  <option value="pending">En attente</option>
                  <option value="confirmed">Confirmées</option>
                  <option value="paid">Payées</option>
                  <option value="cancelled">Annulées</option>
                  <option value="active">Actives</option>
                </select>
              </div>

              <div class="field">
                <span class="field-label">Groupage</span>
                <select v-model="groupBy" class="filter-select-clean">
                  <option value="auto">Auto</option>
                  <option value="day">Jour</option>
                  <option value="week">Semaine</option>
                  <option value="month">Mois</option>
                </select>
              </div>
            </div>
          </div>
        </Transition>
        <button class="btn btn-export btn-sm" :class="{ 'is-loading': exportingPdf }" :disabled="exportingPdf || exportingXls" @click="exportPdf">
          <i class="fas fa-file-pdf"></i> Export PDF
        </button>
        <button class="btn btn-export btn-sm" :class="{ 'is-loading': exportingXls }" :disabled="exportingPdf || exportingXls" @click="exportXls">
          <i class="fas fa-file-excel"></i> Export XLS
        </button>
      </div>
    </div>

    <div class="summary-cards mb-8">
      <div class="summary-card card">
        <div class="summary-icon success"><i class="fas fa-wallet"></i></div>
        <div>
          <span class="label">Revenu Total</span>
          <span class="value success">
            <span v-if="isLoading" class="skeleton-line skeleton-w-70"></span>
            <template v-else>+{{ displayTotalRevenue.toLocaleString() }} Fbu</template>
          </span>
        </div>
      </div>
      <div class="summary-card card">
        <div class="summary-icon primary"><i class="fas fa-chart-line"></i></div>
        <div>
          <span class="label">Revenu (période)</span>
          <span class="value primary">
            <span v-if="isLoading" class="skeleton-line skeleton-w-70"></span>
            <template v-else>+{{ displayRevenueRange.toLocaleString() }} Fbu</template>
          </span>
        </div>
      </div>
      <div class="summary-card card">
        <div class="summary-icon danger"><i class="fas fa-arrow-trend-down"></i></div>
        <div>
          <span class="label">Dépenses (période)</span>
          <span class="value danger">
            <span v-if="isLoading" class="skeleton-line skeleton-w-70"></span>
            <template v-else>-{{ displayExpensesRange.toLocaleString() }} Fbu</template>
          </span>
        </div>
      </div>
      <div class="summary-card card">
        <div class="summary-icon warning"><i class="fas fa-percentage"></i></div>
        <div>
          <span class="label">Marge (période)</span>
          <span class="value warning">
            <span v-if="isLoading" class="skeleton-line skeleton-w-40"></span>
            <template v-else>{{ displayProfitMarginRange.toFixed(1) }}%</template>
          </span>
        </div>
      </div>
    </div>

    <div class="summary-cards mb-8">
      <div class="summary-card card">
        <div class="summary-icon primary"><i class="fas fa-calendar-check"></i></div>
        <div>
          <span class="label">Réservations (Total)</span>
          <span class="value">
            <span v-if="isLoading" class="skeleton-line skeleton-w-30"></span>
            <template v-else>{{ displayBookingTotal }}</template>
          </span>
        </div>
      </div>
      <div class="summary-card card">
        <div class="summary-icon warning"><i class="fas fa-hourglass-half"></i></div>
        <div>
          <span class="label">En attente</span>
          <span class="value warning">
            <span v-if="isLoading" class="skeleton-line skeleton-w-30"></span>
            <template v-else>{{ displayBookingPending }}</template>
          </span>
        </div>
      </div>
      <div class="summary-card card">
        <div class="summary-icon info"><i class="fas fa-circle-check"></i></div>
        <div>
          <span class="label">Confirmées</span>
          <span class="value info">
            <span v-if="isLoading" class="skeleton-line skeleton-w-30"></span>
            <template v-else>{{ displayBookingConfirmed }}</template>
          </span>
        </div>
      </div>
      <div class="summary-card card">
        <div class="summary-icon success"><i class="fas fa-coins"></i></div>
        <div>
          <span class="label">Payées</span>
          <span class="value success">
            <span v-if="isLoading" class="skeleton-line skeleton-w-30"></span>
            <template v-else>{{ displayBookingPaid }}</template>
          </span>
        </div>
      </div>
    </div>

    <div class="charts-grid">
      <div class="chart-card card">
        <div class="card-header">
          <span>Revenus vs Dépenses (période)</span>
        </div>
        <div class="chart-content-clean">
          <div class="chart-stack">
            <div v-show="isLoading" class="skeleton-chart skeleton-overlay"></div>
            <ClientOnly>
              <div class="chart-canvas-wrap" :class="{ 'is-hidden': isLoading }">
                <canvas ref="revenueTotalsEl" class="chart-canvas"></canvas>
              </div>
            </ClientOnly>
          </div>
        </div>
      </div>

      <div class="chart-card card">
        <div class="card-header">
          <span>Occupation (période)</span>
        </div>
        <div class="chart-content-clean charts-stack">
          <div class="chart-stack">
            <div v-show="isLoading" class="skeleton-chart skeleton-overlay"></div>
            <ClientOnly>
              <div class="chart-canvas-wrap chart-canvas-sm" :class="{ 'is-hidden': isLoading }">
                <canvas ref="occupationEl" class="chart-canvas"></canvas>
              </div>
            </ClientOnly>
            <div v-show="!isLoading" class="doughnut-center">
              <div class="doughnut-center-main">{{ displayOccupationRate.toFixed(1) }}%</div>
              <div class="doughnut-center-sub">Taux</div>
            </div>
          </div>
          <div class="legend-clean">
            <div class="legend-item" v-for="item in occupationLegend" :key="item.type">
              <span class="dot" :style="{ background: item.color }"></span>
              <div class="legend-info">
                <span class="legend-label">{{ item.type }}</span>
                <span class="legend-val">{{ item.percentage }}%</span>
              </div>
            </div>
            <div v-if="occupationLegend.length === 0" class="empty-hbar">Aucune donnée</div>
            <div class="range-note" v-if="occupationLegend.length > 0">Taux: {{ displayOccupationRate.toFixed(1) }}%</div>
          </div>
        </div>
      </div>

      <div class="chart-card card">
        <div class="card-header">
          <span>Paiements par Méthode</span>
        </div>
        <div class="chart-content-clean">
          <div class="chart-stack">
            <div v-show="isLoading" class="skeleton-chart skeleton-overlay"></div>
            <ClientOnly>
              <div class="chart-canvas-wrap" :class="{ 'is-hidden': isLoading }">
                <canvas ref="paymentsByMethodEl" class="chart-canvas"></canvas>
              </div>
            </ClientOnly>
          </div>
        </div>
      </div>

      <div class="chart-card card">
        <div class="card-header">
          <span>Réservations par Statut</span>
        </div>
        <div class="chart-content-clean">
          <div class="chart-stack">
            <div v-show="isLoading" class="skeleton-chart skeleton-overlay"></div>
            <ClientOnly>
              <div class="chart-canvas-wrap" :class="{ 'is-hidden': isLoading }">
                <canvas ref="bookingsByStatusEl" class="chart-canvas"></canvas>
              </div>
            </ClientOnly>
          </div>
        </div>
      </div>

      <div class="chart-card card">
        <div class="card-header">
          <span>Évolution (période)</span>
        </div>
        <div class="chart-content-clean">
          <div class="chart-stack">
            <div v-show="isLoading" class="skeleton-chart skeleton-overlay"></div>
            <ClientOnly>
              <div class="chart-canvas-wrap" :class="{ 'is-hidden': isLoading }">
                <canvas ref="evolutionEl" class="chart-canvas"></canvas>
              </div>
            </ClientOnly>
          </div>
        </div>
      </div>

      <div class="chart-card card">
        <div class="card-header">
          <span>Évolution des Réservations (période)</span>
        </div>
        <div class="chart-content-clean">
          <div class="chart-stack">
            <div v-show="isLoading" class="skeleton-chart skeleton-overlay"></div>
            <ClientOnly>
              <div class="chart-canvas-wrap" :class="{ 'is-hidden': isLoading }">
                <canvas ref="bookingsEvolutionEl" class="chart-canvas"></canvas>
              </div>
            </ClientOnly>
          </div>
        </div>
      </div>

      <div class="chart-card card">
        <div class="card-header">
          <span>Réservations par Type</span>
        </div>
        <div class="chart-content-clean charts-stack">
          <div class="chart-stack">
            <div v-show="isLoading" class="skeleton-chart skeleton-overlay"></div>
            <ClientOnly>
              <div class="chart-canvas-wrap chart-canvas-sm" :class="{ 'is-hidden': isLoading }">
                <canvas ref="bookingsByTypeEl" class="chart-canvas"></canvas>
              </div>
            </ClientOnly>
            <div v-show="!isLoading" class="doughnut-center">
              <div class="doughnut-center-main">{{ bookingTypeTopRate.toFixed(1) }}%</div>
              <div class="doughnut-center-sub">Taux</div>
            </div>
          </div>
          <div class="legend-clean">
            <div class="legend-item" v-for="row in bookingsByTypeLegend" :key="row.label">
              <span class="dot" :style="{ background: row.color }"></span>
              <div class="legend-info">
                <span class="legend-label">{{ row.label }}</span>
                <span class="legend-val">{{ row.count }}</span>
              </div>
            </div>
            <div v-if="bookingsByTypeLegend.length === 0" class="empty-hbar">Aucune donnée</div>
          </div>
        </div>
      </div>

      <div class="chart-card card">
        <div class="card-header">
          <span>Matériels par Catégorie</span>
        </div>
        <div class="chart-content-clean">
          <div class="chart-stack">
            <div v-show="isLoading" class="skeleton-chart skeleton-overlay"></div>
            <ClientOnly>
              <div class="chart-canvas-wrap" :class="{ 'is-hidden': isLoading }">
                <canvas ref="materialsByCategoryEl" class="chart-canvas"></canvas>
              </div>
            </ClientOnly>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { api } from '~/composables/useApi'

definePageMeta({ layout: 'admin' })

const stats = ref({
  total_revenue: 0,
  revenue_last_28_days: 0,
  expenses_last_28_days: 0,
  occupation_rate_28_days: 0,
  occupation_data: [],
  range_start: '',
  range_end: '',
  range_days: 28,
  revenue_in_range: 0,
  expenses_in_range: 0,
  occupation_rate_in_range: 0,
  occupation_data_in_range: []
})

const bookings = ref([])
const payments = ref([])
const expenses = ref([])
const materials = ref([])
const exportingPdf = ref(false)
const exportingXls = ref(false)
const loadingStats = ref(false)
const loadingBookings = ref(false)
const loadingPayments = ref(false)
const loadingExpenses = ref(false)
const loadingMaterials = ref(false)
const isMobile = ref(false)
const filtersOpen = ref(false)
const chartsReady = ref(false)

const preset = ref('28d')
const customStart = ref('')
const customEnd = ref('')
const paymentStatusFilter = ref('all')
const bookingStatusFilter = ref('active')
const groupBy = ref('auto')

const revenueTotalsEl = ref(null)
const occupationEl = ref(null)
const paymentsByMethodEl = ref(null)
const bookingsByStatusEl = ref(null)
const evolutionEl = ref(null)
const bookingsEvolutionEl = ref(null)
const bookingsByTypeEl = ref(null)
const materialsByCategoryEl = ref(null)

const isLoading = computed(() => loadingStats.value || loadingBookings.value || loadingPayments.value || loadingExpenses.value || loadingMaterials.value)

const toYmd = (d) => {
  const dt = (d instanceof Date) ? d : new Date(d)
  if (Number.isNaN(dt.getTime())) return ''
  const y = dt.getFullYear()
  const m = String(dt.getMonth() + 1).padStart(2, '0')
  const day = String(dt.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

const addDays = (ymd, days) => {
  const base = new Date(`${ymd}T00:00:00`)
  base.setDate(base.getDate() + days)
  return toYmd(base)
}

const formatMoney = (v) => `${Number(v || 0).toLocaleString()} Fbu`

const resolvePreset = (value) => {
  const todayYmd = toYmd(new Date())
  if (value === '7d') return { start: addDays(todayYmd, -6), end: todayYmd }
  if (value === '28d') return { start: addDays(todayYmd, -27), end: todayYmd }
  if (value === '90d') return { start: addDays(todayYmd, -89), end: todayYmd }
  if (value === 'year') {
    const now = new Date()
    const start = `${now.getFullYear()}-01-01`
    return { start, end: todayYmd }
  }
  if (value === 'this_month') {
    const now = new Date()
    const start = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-01`
    return { start, end: todayYmd }
  }
  if (value === 'last_month') {
    const now = new Date()
    const firstThisMonth = new Date(now.getFullYear(), now.getMonth(), 1)
    const lastPrevMonth = new Date(firstThisMonth)
    lastPrevMonth.setDate(0)
    const startPrevMonth = new Date(lastPrevMonth.getFullYear(), lastPrevMonth.getMonth(), 1)
    return { start: toYmd(startPrevMonth), end: toYmd(lastPrevMonth) }
  }
  if (value === 'custom') {
    const start = String(customStart.value || '').slice(0, 10)
    const end = String(customEnd.value || '').slice(0, 10)
    if (start && end && end >= start) return { start, end }
    return resolvePreset('28d')
  }
  return resolvePreset('28d')
}

const activeRange = computed(() => resolvePreset(preset.value))
const rangeStartYmd = computed(() => activeRange.value.start)
const rangeEndYmd = computed(() => activeRange.value.end)
const rangeLabel = computed(() => (rangeStartYmd.value && rangeEndYmd.value) ? `${rangeStartYmd.value} → ${rangeEndYmd.value}` : '')
const rangeDays = computed(() => {
  if (!rangeStartYmd.value || !rangeEndYmd.value) return 0
  const a = new Date(`${rangeStartYmd.value}T00:00:00`)
  const b = new Date(`${rangeEndYmd.value}T00:00:00`)
  const diff = Math.floor((b.getTime() - a.getTime()) / (24 * 60 * 60 * 1000))
  return diff >= 0 ? diff + 1 : 0
})

const rangeGrouping = computed(() => {
  if (groupBy.value !== 'auto') return groupBy.value
  const d = rangeDays.value
  if (d <= 31) return 'day'
  if (d <= 140) return 'week'
  return 'month'
})

const dateOverlapsRange = (start, end, rangeStart, rangeEnd) => {
  const s = String(start || '').slice(0, 10)
  const e = String(end || '').slice(0, 10)
  if (!s || !e || !rangeStart || !rangeEnd) return false
  return s <= rangeEnd && e >= rangeStart
}

const inRangeYmd = (ymd, rangeStart, rangeEnd) => {
  const v = String(ymd || '').slice(0, 10)
  if (!v || !rangeStart || !rangeEnd) return false
  return v >= rangeStart && v <= rangeEnd
}

const filteredPayments = computed(() => {
  const start = rangeStartYmd.value
  const end = rangeEndYmd.value
  const status = paymentStatusFilter.value
  return (payments.value || []).filter((p) => {
    if (!inRangeYmd(p.date, start, end)) return false
    if (status !== 'all' && String(p.status || '') !== status) return false
    return true
  })
})

const filteredPaymentsPaid = computed(() => {
  const start = rangeStartYmd.value
  const end = rangeEndYmd.value
  return (payments.value || []).filter((p) => inRangeYmd(p.date, start, end) && String(p.status || '') === 'paid')
})

const filteredExpenses = computed(() => {
  const start = rangeStartYmd.value
  const end = rangeEndYmd.value
  return (expenses.value || []).filter((e) => inRangeYmd(e.date, start, end))
})

const materialsByCategoryLegend = computed(() => {
  const map = new Map()
  for (const m of materials.value || []) {
    const key = String(m.category || 'Autre')
    const prev = map.get(key) || { category: key, available: 0, damaged: 0, lost: 0, total: 0 }
    const available = Number(m.available_quantity || 0)
    const damaged = Number(m.damaged_quantity || 0)
    const lost = Number(m.lost_quantity || 0)
    const total = Number(m.total_quantity || 0)
    map.set(key, {
      category: key,
      available: prev.available + available,
      damaged: prev.damaged + damaged,
      lost: prev.lost + lost,
      total: prev.total + total,
    })
  }

  const rows = Array.from(map.values()).sort((a, b) => b.total - a.total)
  const top = rows.slice(0, 8)
  const rest = rows.slice(8)
  if (rest.length) {
    const other = rest.reduce((acc, r) => ({
      category: 'Autre',
      available: acc.available + r.available,
      damaged: acc.damaged + r.damaged,
      lost: acc.lost + r.lost,
      total: acc.total + r.total,
    }), { category: 'Autre', available: 0, damaged: 0, lost: 0, total: 0 })
    top.push(other)
  }
  return top
})

const filteredBookings = computed(() => {
  const start = rangeStartYmd.value
  const end = rangeEndYmd.value
  const status = bookingStatusFilter.value
  return (bookings.value || []).filter((b) => {
    if (!dateOverlapsRange(b.start_date, b.end_date, start, end)) return false
    const st = String(b.status || '')
    if (status === 'all') return true
    if (status === 'active') return ['pending', 'confirmed', 'paid'].includes(st)
    return st === status
  })
})

const bookingCounts = computed(() => {
  const counts = { total: 0, pending: 0, confirmed: 0, paid: 0, cancelled: 0 }
  for (const b of filteredBookings.value || []) {
    counts.total += 1
    if (b.status === 'pending') counts.pending += 1
    if (b.status === 'confirmed') counts.confirmed += 1
    if (b.status === 'paid') counts.paid += 1
    if (b.status === 'cancelled') counts.cancelled += 1
  }
  return counts
})

const revenueInRange = computed(() => Number(stats.value.revenue_in_range || stats.value.revenue_last_28_days || 0))
const expensesInRange = computed(() => Number(stats.value.expenses_in_range || stats.value.expenses_last_28_days || 0))
const profitMarginInRange = computed(() => {
  const revenue = Number(revenueInRange.value || 0)
  const expensesV = Number(expensesInRange.value || 0)
  if (revenue === 0) return 0
  const margin = ((revenue - expensesV) / revenue) * 100
  return Number(margin.toFixed(1))
})

const occupationRate = computed(() => {
  const v = Number(stats.value.occupation_rate_in_range || stats.value.occupation_rate_28_days || 0)
  return Number.isFinite(v) ? v : 0
})

const occupationLegend = computed(() => {
  const colors = ['#0f172a', '#22c55e', '#f59e0b', '#0ea5e9', '#ef4444', '#6366f1']
  const source = stats.value.occupation_data_in_range?.length ? stats.value.occupation_data_in_range : (stats.value.occupation_data || [])
  const items = (source || [])
    .map((i) => ({ type: i.type, percentage: Number(i.percentage || 0) }))
    .filter((i) => i.percentage > 0)
  return items.map((item, idx) => ({ ...item, color: colors[idx % colors.length] }))
})

const paymentsByMethodLegend = computed(() => {
  const map = new Map()
  for (const p of filteredPayments.value || []) {
    const key = String(p.method || 'Autre')
    map.set(key, (map.get(key) || 0) + 1)
  }
  const rows = Array.from(map.entries()).map(([label, count]) => ({ label, count }))
    .sort((a, b) => b.count - a.count)
  const colors = ['#0ea5e9', '#22c55e', '#f59e0b', '#ef4444', '#6366f1', '#0f172a']
  return rows.map((r, idx) => ({ ...r, color: colors[idx % colors.length] }))
})

const bookingsByStatusLegend = computed(() => {
  const counts = bookingCounts.value
  return [
    { key: 'paid', label: 'Payées', count: counts.paid, color: '#22c55e' },
    { key: 'confirmed', label: 'Confirmées', count: counts.confirmed, color: '#0ea5e9' },
    { key: 'pending', label: 'En attente', count: counts.pending, color: '#f59e0b' },
    { key: 'cancelled', label: 'Annulées', count: counts.cancelled, color: '#ef4444' },
  ].filter(r => r.count > 0)
})

const bookingsByTypeLegend = computed(() => {
  const map = new Map()
  for (const b of filteredBookings.value || []) {
    const key = String(b.event_type || 'Autre')
    map.set(key, (map.get(key) || 0) + 1)
  }
  const rows = Array.from(map.entries()).map(([label, count]) => ({ label, count }))
    .sort((a, b) => b.count - a.count)
  const colors = ['#0f172a', '#0ea5e9', '#22c55e', '#f59e0b', '#ef4444', '#6366f1']
  return rows.map((r, idx) => ({ ...r, color: colors[idx % colors.length] }))
})

const bookingTypeTopRate = computed(() => {
  const rows = bookingsByTypeLegend.value || []
  const total = rows.reduce((sum, r) => sum + Number(r.count || 0), 0)
  if (total <= 0) return 0
  const max = Math.max(0, ...rows.map(r => Number(r.count || 0)))
  return Number(((max / total) * 100).toFixed(1))
})

const bookingEvolutionTypes = computed(() => {
  const map = new Map()
  for (const b of filteredBookings.value || []) {
    const key = String(b.event_type || 'Autre')
    map.set(key, (map.get(key) || 0) + 1)
  }
  const rows = Array.from(map.entries()).map(([type, count]) => ({ type, count }))
    .sort((a, b) => b.count - a.count)

  const top = rows.slice(0, 5).map(r => r.type)
  if (rows.length > 5 && !top.includes('Autre')) top.push('Autre')
  return top
})

const buildBuckets = (startYmd, endYmd, grouping) => {
  if (!startYmd || !endYmd) return []
  const out = []
  if (grouping === 'day') {
    let cur = startYmd
    while (cur <= endYmd) {
      out.push({ key: cur, label: cur, start: cur, end: cur })
      cur = addDays(cur, 1)
    }
    return out
  }

  if (grouping === 'week') {
    let cur = startYmd
    while (cur <= endYmd) {
      const bucketStart = cur
      const bucketEnd = addDays(cur, 6)
      const end = bucketEnd > endYmd ? endYmd : bucketEnd
      out.push({ key: bucketStart, label: `${bucketStart} → ${end}`, start: bucketStart, end })
      cur = addDays(cur, 7)
    }
    return out
  }

  const startDate = new Date(`${startYmd}T00:00:00`)
  const endDate = new Date(`${endYmd}T00:00:00`)
  const curDate = new Date(startDate.getFullYear(), startDate.getMonth(), 1)
  while (curDate.getTime() <= endDate.getTime()) {
    const bucketStart = toYmd(curDate)
    const nextMonth = new Date(curDate.getFullYear(), curDate.getMonth() + 1, 1)
    const bucketEndDate = new Date(nextMonth)
    bucketEndDate.setDate(0)
    const bucketEnd = toYmd(bucketEndDate)
    const start = bucketStart < startYmd ? startYmd : bucketStart
    const end = bucketEnd > endYmd ? endYmd : bucketEnd
    const label = `${String(curDate.getFullYear())}-${String(curDate.getMonth() + 1).padStart(2, '0')}`
    out.push({ key: label, label, start, end })
    curDate.setMonth(curDate.getMonth() + 1)
  }
  return out
}

const evolutionSeries = computed(() => {
  const buckets = buildBuckets(rangeStartYmd.value, rangeEndYmd.value, rangeGrouping.value)
  const revenues = []
  const expensesSeries = []
  for (const b of buckets) {
    let rev = 0
    for (const p of filteredPaymentsPaid.value || []) {
      const d = String(p.date || '').slice(0, 10)
      if (d >= b.start && d <= b.end) rev += Number(p.amount || 0)
    }
    let exp = 0
    for (const e of filteredExpenses.value || []) {
      const d = String(e.date || '').slice(0, 10)
      if (d >= b.start && d <= b.end) exp += Number(e.amount || 0)
    }
    revenues.push(rev)
    expensesSeries.push(exp)
  }
  return {
    labels: buckets.map(b => b.label),
    revenues,
    expenses: expensesSeries
  }
})

const bookingsEvolutionSeries = computed(() => {
  const buckets = buildBuckets(rangeStartYmd.value, rangeEndYmd.value, rangeGrouping.value)
  const counts = []
  for (const b of buckets) {
    let c = 0
    for (const booking of filteredBookings.value || []) {
      const d = String(booking.start_date || '').slice(0, 10)
      if (!d) continue
      if (d >= b.start && d <= b.end) c += 1
    }
    counts.push(c)
  }
  return {
    labels: buckets.map(b => b.start),
    counts
  }
})

const bookingsEvolutionByTypeSeries = computed(() => {
  const buckets = buildBuckets(rangeStartYmd.value, rangeEndYmd.value, rangeGrouping.value)
  const types = bookingEvolutionTypes.value || []
  const dataByType = new Map(types.map(t => [t, new Array(buckets.length).fill(0)]))

  for (const booking of filteredBookings.value || []) {
    const d = String(booking.start_date || '').slice(0, 10)
    if (!d) continue
    let bucketIndex = -1
    for (let i = 0; i < buckets.length; i += 1) {
      const b = buckets[i]
      if (d >= b.start && d <= b.end) {
        bucketIndex = i
        break
      }
    }
    if (bucketIndex === -1) continue

    const type = String(booking.event_type || 'Autre')
    const key = dataByType.has(type) ? type : (dataByType.has('Autre') ? 'Autre' : null)
    if (!key) continue
    dataByType.get(key)[bucketIndex] += 1
  }

  const palette = ['rgba(14,165,233,0.75)', 'rgba(34,197,94,0.75)', 'rgba(245,158,11,0.75)', 'rgba(239,68,68,0.75)', 'rgba(99,102,241,0.75)', 'rgba(15,23,42,0.75)']
  const datasets = types.map((t, idx) => ({
    label: t,
    data: dataByType.get(t) || new Array(buckets.length).fill(0),
    backgroundColor: palette[idx % palette.length],
    borderRadius: 8,
    borderSkipped: false,
  }))

  return {
    labels: buckets.map(b => b.start),
    datasets
  }
})

const exportXls = async () => {
  exportingXls.value = true
  await nextTick()
  const rows = [
    ['Période', rangeLabel.value],
    ['Revenu Total', String(stats.value.total_revenue || 0)],
    ['Revenu (période)', String(revenueInRange.value || 0)],
    ['Dépenses (période)', String(expensesInRange.value || 0)],
    ['Marge (période) (%)', String(profitMarginInRange.value || 0)],
    ['Occupation (période) (%)', String(occupationRate.value || 0)],
    ['Réservations (période - Total)', String(bookingCounts.value.total)],
    ['Réservations (En attente)', String(bookingCounts.value.pending)],
    ['Réservations (Confirmées)', String(bookingCounts.value.confirmed)],
    ['Réservations (Payées)', String(bookingCounts.value.paid)],
    ['Réservations (Annulées)', String(bookingCounts.value.cancelled)],
    ['Paiements (période - Total)', String(filteredPayments.value.length)],
  ]

  const table = [
    '<table>',
    '<thead><tr><th>Indicateur</th><th>Valeur</th></tr></thead>',
    '<tbody>',
    ...rows.map(r => `<tr><td>${r[0]}</td><td>${r[1]}</td></tr>`),
    '</tbody>',
    '</table>'
  ].join('')

  const html = `<!doctype html><html><head><meta charset="utf-8"></head><body>${table}</body></html>`
  const blob = new Blob([html], { type: 'application/vnd.ms-excel' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'reports.xls'
  a.click()
  URL.revokeObjectURL(url)
  setTimeout(() => {
    exportingXls.value = false
  }, 350)
}

const exportPdf = async () => {
  exportingPdf.value = true
  await nextTick()
  const rows = [
    ['Période', rangeLabel.value],
    ['Revenu Total', `${Number(stats.value.total_revenue || 0).toLocaleString()} Fbu`],
    ['Revenu (période)', `${Number(revenueInRange.value || 0).toLocaleString()} Fbu`],
    ['Dépenses (période)', `${Number(expensesInRange.value || 0).toLocaleString()} Fbu`],
    ['Marge (période)', `${profitMarginInRange.value || 0}%`],
    ['Occupation (période)', `${occupationRate.value || 0}%`],
    ['Réservations (période - Total)', String(bookingCounts.value.total)],
    ['En attente', String(bookingCounts.value.pending)],
    ['Confirmées', String(bookingCounts.value.confirmed)],
    ['Payées', String(bookingCounts.value.paid)],
    ['Annulées', String(bookingCounts.value.cancelled)],
    ['Paiements (période - Total)', String(filteredPayments.value.length)],
  ]

  const table = [
    '<table>',
    '<thead><tr><th>Indicateur</th><th>Valeur</th></tr></thead>',
    '<tbody>',
    ...rows.map(r => `<tr><td>${r[0]}</td><td>${r[1]}</td></tr>`),
    '</tbody>',
    '</table>'
  ].join('')

  const win = window.open('', '_blank')
  if (!win) {
    exportingPdf.value = false
    return
  }
  win.document.write(`<!doctype html><html><head><meta charset="utf-8"><title>Rapports</title><style>
  body{font-family:Arial, sans-serif; padding:20px}
  table{width:100%; border-collapse:collapse}
  th,td{border:1px solid #e2e8f0; padding:8px; text-align:left; font-size:12px}
  th{background:#f8fafc}
  </style></head><body><h2>Rapports et Statistiques</h2>${table}</body></html>`)
  win.document.close()
  win.focus()
  win.print()
  win.close()
  setTimeout(() => {
    exportingPdf.value = false
  }, 350)
}

const fetchStats = async () => {
  loadingStats.value = true
  try {
    const response = await api.get('summary/', { params: { start_date: rangeStartYmd.value, end_date: rangeEndYmd.value } })
    stats.value = response.data
  } catch (error) {
    stats.value = { ...stats.value, revenue_in_range: 0, expenses_in_range: 0, occupation_rate_in_range: 0, occupation_data_in_range: [] }
  } finally {
    loadingStats.value = false
  }
}

const fetchBookings = async () => {
  loadingBookings.value = true
  try {
    const { data } = await api.get('bookings/')
    bookings.value = data
  } catch (error) {
    bookings.value = []
  } finally {
    loadingBookings.value = false
  }
}

const fetchPayments = async () => {
  loadingPayments.value = true
  try {
    const { data } = await api.get('payments/')
    payments.value = data
  } catch (error) {
    payments.value = []
  } finally {
    loadingPayments.value = false
  }
}

const fetchExpenses = async () => {
  loadingExpenses.value = true
  try {
    const { data } = await api.get('expenses/')
    expenses.value = data
  } catch (error) {
    expenses.value = []
  } finally {
    loadingExpenses.value = false
  }
}

const fetchMaterials = async () => {
  loadingMaterials.value = true
  try {
    const { data } = await api.get('materials/')
    materials.value = data
  } catch (error) {
    materials.value = []
  } finally {
    loadingMaterials.value = false
  }
}

const chartLib = shallowRef(null)
const chartInstances = new Map()

const loadChartJs = async () => {
  if (chartLib.value) return chartLib.value
  const mod = await import('chart.js/auto')
  chartLib.value = mod.default
  return chartLib.value
}

const upsertChart = async (key, canvasEl, cfg) => {
  if (!process.client) return
  if (!canvasEl) return
  const Chart = await loadChartJs()
  const existing = chartInstances.get(key)
  if (existing && existing.canvas !== canvasEl) {
    existing.destroy()
    chartInstances.delete(key)
  }
  if (!existing) {
    chartInstances.set(key, new Chart(canvasEl, cfg))
    return
  }
  existing.data = cfg.data
  existing.options = cfg.options
  existing.update()
}

let renderRaf = null
const scheduleRender = () => {
  if (!process.client) return
  if (renderRaf) return
  renderRaf = requestAnimationFrame(async () => {
    renderRaf = null
    await nextTick()
    renderCharts()
  })
}

const renderCharts = async () => {
  if (!process.client) return
  if (isLoading.value) return

  const revenue = Number(revenueInRange.value || 0)
  const expensesV = Number(expensesInRange.value || 0)
  await upsertChart('revenueTotals', revenueTotalsEl.value, {
    type: 'bar',
    data: {
      labels: ['Revenus', 'Dépenses'],
      datasets: [
        {
          label: 'Montant',
          data: [revenue, expensesV],
          backgroundColor: ['rgba(34,197,94,0.85)', 'rgba(239,68,68,0.85)'],
          borderRadius: 10,
          borderSkipped: false,
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: { duration: 850, easing: 'easeOutQuart' },
      plugins: {
        legend: { display: false },
        tooltip: { callbacks: { label: (ctx) => formatMoney(ctx.parsed.y) } }
      },
      scales: {
        y: { ticks: { callback: (v) => formatMoney(v) }, grid: { color: 'rgba(148,163,184,0.22)' } },
        x: { grid: { display: false } }
      }
    }
  })

  const occ = occupationLegend.value
  const occData = occ.length ? occ.map(i => i.percentage) : [1]
  const occLabels = occ.length ? occ.map(i => i.type) : ['Aucune donnée']
  const occColors = occ.length ? occ.map(i => i.color) : ['#e2e8f0']
  await upsertChart('occupation', occupationEl.value, {
    type: 'doughnut',
    data: {
      labels: occLabels,
      datasets: [
        {
          data: occData,
          backgroundColor: occColors,
          borderWidth: 0,
          hoverOffset: 6,
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '68%',
      animation: { duration: 900, easing: 'easeOutQuart' },
      plugins: {
        legend: { display: false },
        tooltip: { callbacks: { label: (ctx) => `${ctx.label}: ${Number(ctx.parsed || 0).toFixed(1)}%` } }
      }
    }
  })

  const pm = paymentsByMethodLegend.value
  const pmLabels = pm.length ? pm.map(r => r.label) : ['Aucune donnée']
  const pmData = pm.length ? pm.map(r => r.count) : [0]
  const pmColors = pm.length ? pm.map(r => r.color) : ['#e2e8f0']
  await upsertChart('paymentsByMethod', paymentsByMethodEl.value, {
    type: 'bar',
    data: {
      labels: pmLabels,
      datasets: [
        {
          label: 'Paiements',
          data: pmData,
          backgroundColor: pmColors,
          borderRadius: 10,
          borderSkipped: false,
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      indexAxis: 'y',
      animation: { duration: 850, easing: 'easeOutQuart' },
      plugins: {
        legend: { display: false }
      },
      scales: {
        x: { ticks: { precision: 0 }, grid: { color: 'rgba(148,163,184,0.22)' } },
        y: { grid: { display: false } }
      }
    }
  })

  const bs = bookingsByStatusLegend.value
  const bsLabels = bs.length ? bs.map(r => r.label) : ['Aucune donnée']
  const bsData = bs.length ? bs.map(r => r.count) : [0]
  const bsColors = bs.length ? bs.map(r => r.color) : ['#e2e8f0']
  await upsertChart('bookingsByStatus', bookingsByStatusEl.value, {
    type: 'bar',
    data: {
      labels: bsLabels,
      datasets: [
        {
          label: 'Réservations',
          data: bsData,
          backgroundColor: bsColors,
          borderRadius: 10,
          borderSkipped: false,
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      indexAxis: 'y',
      animation: { duration: 850, easing: 'easeOutQuart' },
      plugins: {
        legend: { display: false }
      },
      scales: {
        x: { ticks: { precision: 0 }, grid: { color: 'rgba(148,163,184,0.22)' } },
        y: { grid: { display: false } }
      }
    }
  })

  const evo = evolutionSeries.value
  const evoHasAny = (evo.labels || []).length > 0
  await upsertChart('evolution', evolutionEl.value, {
    type: 'bar',
    data: {
      labels: evoHasAny ? evo.labels : ['Aucune donnée'],
      datasets: [
        {
          label: 'Revenus',
          data: evoHasAny ? evo.revenues : [0],
          backgroundColor: 'rgba(34,197,94,0.75)',
          borderRadius: 8,
          borderSkipped: false,
        },
        {
          label: 'Dépenses',
          data: evoHasAny ? evo.expenses : [0],
          backgroundColor: 'rgba(239,68,68,0.75)',
          borderRadius: 8,
          borderSkipped: false,
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: { duration: 900, easing: 'easeOutQuart' },
      plugins: {
        legend: { position: 'bottom' },
        tooltip: { callbacks: { label: (ctx) => `${ctx.dataset.label}: ${formatMoney(ctx.parsed.y)}` } }
      },
      scales: {
        y: { ticks: { callback: (v) => formatMoney(v) }, grid: { color: 'rgba(148,163,184,0.22)' } },
        x: { grid: { display: false } }
      }
    }
  })

  const be = bookingsEvolutionSeries.value
  const beType = bookingsEvolutionByTypeSeries.value
  const beHasAny = (beType.labels || []).length > 0
  await upsertChart('bookingsEvolution', bookingsEvolutionEl.value, {
    type: 'bar',
    data: {
      labels: beHasAny ? beType.labels : ['Aucune donnée'],
      datasets: beHasAny ? beType.datasets : [{ label: 'Réservations', data: [0], backgroundColor: 'rgba(226,232,240,1)', borderRadius: 8, borderSkipped: false }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: { duration: 900, easing: 'easeOutQuart' },
      plugins: {
        legend: { position: 'bottom' }
      },
      scales: {
        y: { stacked: true, ticks: { precision: 0 }, grid: { color: 'rgba(148,163,184,0.22)' } },
        x: {
          stacked: true,
          grid: { display: false },
          ticks: { maxRotation: 0, autoSkip: true, maxTicksLimit: 8 }
        }
      }
    }
  })

  const bt = bookingsByTypeLegend.value
  const btLabels = bt.length ? bt.map(r => r.label) : ['Aucune donnée']
  const btData = bt.length ? bt.map(r => r.count) : [1]
  const btColors = bt.length ? bt.map(r => r.color) : ['#e2e8f0']
  await upsertChart('bookingsByType', bookingsByTypeEl.value, {
    type: 'doughnut',
    data: {
      labels: btLabels,
      datasets: [
        {
          data: btData,
          backgroundColor: btColors,
          borderWidth: 0,
          hoverOffset: 6,
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '64%',
      animation: { duration: 900, easing: 'easeOutQuart' },
      plugins: {
        legend: { display: false }
      }
    }
  })

  const mats = materialsByCategoryLegend.value
  const matsHas = mats.length > 0
  await upsertChart('materialsByCategory', materialsByCategoryEl.value, {
    type: 'bar',
    data: {
      labels: matsHas ? mats.map(r => r.category) : ['Aucune donnée'],
      datasets: matsHas ? [
        { label: 'Disponible', data: mats.map(r => r.available), backgroundColor: 'rgba(34,197,94,0.75)', borderRadius: 8, borderSkipped: false },
        { label: 'Endommagé', data: mats.map(r => r.damaged), backgroundColor: 'rgba(245,158,11,0.75)', borderRadius: 8, borderSkipped: false },
        { label: 'Perdu', data: mats.map(r => r.lost), backgroundColor: 'rgba(239,68,68,0.75)', borderRadius: 8, borderSkipped: false },
      ] : [
        { label: 'Matériels', data: [0], backgroundColor: 'rgba(226,232,240,1)', borderRadius: 8, borderSkipped: false }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      indexAxis: 'y',
      animation: { duration: 900, easing: 'easeOutQuart' },
      plugins: {
        legend: { position: 'bottom' },
        tooltip: {
          callbacks: {
            label: (ctx) => `${ctx.dataset.label}: ${Number(ctx.parsed.x || 0)}`
          }
        }
      },
      scales: {
        x: { stacked: true, ticks: { precision: 0 }, grid: { color: 'rgba(148,163,184,0.22)' } },
        y: { stacked: true, grid: { display: false } }
      }
    }
  })
}

let statsTimer = null
watch([rangeStartYmd, rangeEndYmd], () => {
  if (statsTimer) clearTimeout(statsTimer)
  statsTimer = setTimeout(() => {
    fetchStats()
  }, 180)
}, { immediate: true })

watch([filteredBookings, filteredPayments, filteredExpenses, occupationLegend, paymentsByMethodLegend, bookingsByTypeLegend, bookingEvolutionTypes, materialsByCategoryLegend], () => {
  scheduleRender()
}, { deep: true })

watch([revenueInRange, expensesInRange, occupationRate], () => {
  scheduleRender()
})

watch(isLoading, (v) => {
  if (!process.client) return
  if (v) return
  scheduleRender()
})

watch(
  () => [
    revenueTotalsEl.value,
    occupationEl.value,
    paymentsByMethodEl.value,
    bookingsByStatusEl.value,
    evolutionEl.value,
    bookingsEvolutionEl.value,
    bookingsByTypeEl.value,
    materialsByCategoryEl.value,
  ],
  (els) => {
    if (!process.client) return
    if (els.some(Boolean)) scheduleRender()
  },
  { immediate: true }
)

onMounted(() => {
  const initial = resolvePreset('28d')
  customStart.value = initial.start
  customEnd.value = initial.end
  fetchBookings()
  fetchPayments()
  fetchExpenses()
  fetchMaterials()
  nextTick(() => { chartsReady.value = true })
  nextTick(() => { scheduleRender() })
  if (process.client) {
    const update = () => {
      const nextIsMobile = window.innerWidth <= 992
      if (nextIsMobile !== isMobile.value) {
        isMobile.value = nextIsMobile
        filtersOpen.value = !nextIsMobile
      } else {
        isMobile.value = nextIsMobile
      }
    }
    update()
    window.addEventListener('resize', update)
    onBeforeUnmount(() => window.removeEventListener('resize', update))
  }
})

const displayTotalRevenue = ref(0)
const displayRevenueRange = ref(0)
const displayExpensesRange = ref(0)
const displayProfitMarginRange = ref(0)
const displayOccupationRate = ref(0)
const displayBookingTotal = ref(0)
const displayBookingPending = ref(0)
const displayBookingConfirmed = ref(0)
const displayBookingPaid = ref(0)

const rafMap = new Map()
const animateCounter = (outRef, toValue, decimals = 0) => {
  const d = Math.max(0, Math.min(3, Number(decimals) || 0))
  if (typeof requestAnimationFrame === 'undefined' || typeof cancelAnimationFrame === 'undefined') {
    const n = Number(toValue || 0)
    outRef.value = Number.isFinite(n) ? Number(n.toFixed(d)) : 0
    return
  }

  const from = Number(outRef.value || 0)
  const to = Number(toValue || 0)
  const duration = 750
  const start = (typeof performance !== 'undefined' && typeof performance.now === 'function') ? performance.now() : Date.now()
  const existing = rafMap.get(outRef)
  if (existing) cancelAnimationFrame(existing)

  const easeOutCubic = (t) => 1 - Math.pow(1 - t, 3)
  const step = (now) => {
    const p = Math.min(1, (now - start) / duration)
    const eased = easeOutCubic(p)
    const current = from + (to - from) * eased
    outRef.value = Number(current.toFixed(d))
    if (p < 1) rafMap.set(outRef, requestAnimationFrame(step))
  }

  rafMap.set(outRef, requestAnimationFrame(step))
}

watch(() => Number(stats.value.total_revenue || 0), (v) => animateCounter(displayTotalRevenue, v), { immediate: true })
watch(revenueInRange, (v) => animateCounter(displayRevenueRange, v), { immediate: true })
watch(expensesInRange, (v) => animateCounter(displayExpensesRange, v), { immediate: true })
watch(profitMarginInRange, (v) => animateCounter(displayProfitMarginRange, v, 1), { immediate: true })
watch(occupationRate, (v) => animateCounter(displayOccupationRate, v, 1), { immediate: true })
watch(() => bookingCounts.value.total, (v) => animateCounter(displayBookingTotal, v), { immediate: true })
watch(() => bookingCounts.value.pending, (v) => animateCounter(displayBookingPending, v), { immediate: true })
watch(() => bookingCounts.value.confirmed, (v) => animateCounter(displayBookingConfirmed, v), { immediate: true })
watch(() => bookingCounts.value.paid, (v) => animateCounter(displayBookingPaid, v), { immediate: true })

onBeforeUnmount(() => {
  for (const id of rafMap.values()) cancelAnimationFrame(id)
  if (renderRaf) cancelAnimationFrame(renderRaf)
  for (const chart of chartInstances.values()) chart.destroy()
  chartInstances.clear()
  if (statsTimer) clearTimeout(statsTimer)
})
</script>

<style scoped>
.admin-reports {
  padding: 0;
}

.header-actions {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--space-10);
  gap: var(--space-4);
  flex-wrap: wrap;
}

.header-actions h1 {
  font-size: 1.75rem;
  font-weight: 800;
  color: #0f172a;
  margin-bottom: 0.25rem;
}

.subtitle {
  color: #64748b;
  font-size: 0.9rem;
  font-weight: 500;
}

.range-pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-weight: 800;
  color: #0f172a;
}

.filters-group {
  display: flex;
  gap: var(--space-3);
  align-items: center;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.filters-panel {
  display: flex;
  align-items: center;
  padding: 10px 12px;
  border: 1px solid #e2e8f0;
  border-radius: var(--rounded-lg);
  background: #ffffff;
}

.filters-row {
  display: flex;
  align-items: flex-end;
  gap: var(--space-3);
  flex-wrap: wrap;
}

.field {
  display: grid;
  gap: 6px;
}

.field-label {
  font-size: 0.7rem;
  font-weight: 800;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.filter-input-clean {
  padding: 0.5rem 1rem;
  border: 1px solid #e2e8f0;
  border-radius: var(--rounded-md);
  font-size: 0.85rem;
  background: white;
  color: #475569;
  font-weight: 700;
}

.filters-fade-enter-active,
.filters-fade-leave-active {
  transition: opacity .18s ease, transform .18s ease;
}

.filters-fade-enter-from,
.filters-fade-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}

.filter-select-clean {
  padding: 0.5rem 2rem 0.5rem 1rem;
  border: 1px solid #e2e8f0;
  border-radius: var(--rounded-md);
  font-size: 0.85rem;
  background: white;
  color: #475569;
  font-weight: 600;
  cursor: pointer;
}

.filters-toggle {
  display: none;
  width: 42px;
  height: 42px;
  border: 1px solid #e2e8f0;
  background: #f8fafc;
  color: #475569;
}

.filters-toggle.active {
  background: rgba(212, 175, 55, .18);
  border-color: rgba(212, 175, 55, .35);
  color: #0f172a;
}

@media (max-width: 992px) {
  .filters-toggle {
    display: inline-flex;
    align-items: center;
    justify-content: center;
  }

  .header-actions h1 {
    font-size: 1.35rem;
  }

  .summary-cards {
    grid-template-columns: 1fr;
    gap: var(--space-4);
  }

  .summary-card {
    padding: var(--space-5);
  }

  .charts-grid {
    grid-template-columns: 1fr;
    gap: var(--space-6);
  }

  .chart-card {
    padding: var(--space-5);
    min-height: auto;
  }

  .card-header {
    margin-bottom: var(--space-6);
  }
}

.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: var(--space-6);
}

.summary-card {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-6);
}

.summary-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
}

.summary-icon.success { background: #f0fdf4; color: #22c55e; }
.summary-icon.danger { background: #fef2f2; color: #ef4444; }
.summary-icon.primary { background: #f1f5f9; color: #0f172a; }
.summary-icon.info { background: #f0f9ff; color: #0ea5e9; }
.summary-icon.warning { background: #fffbeb; color: #f59e0b; }

.label {
  display: block;
  font-size: 0.7rem;
  color: #94a3b8;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.value {
  font-size: 1.25rem;
  font-weight: 800;
  color: #0f172a;
}

.value.success { color: #16a34a; }
.value.danger { color: #ef4444; }
.value.warning { color: #d97706; }
.value.info { color: #0ea5e9; }
.value.primary { color: #0f172a; }

.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
  gap: var(--space-8);
}

.chart-card {
  padding: var(--space-8);
  min-height: 450px;
  display: flex;
  flex-direction: column;
}

.card-header {
  border: none;
  padding: 0;
  margin-bottom: var(--space-10);
  font-size: 1.1rem;
}

.chart-content-clean {
  flex: 1;
  display: flex;
  align-items: stretch;
  justify-content: center;
}

.charts-stack {
  flex-direction: column;
  gap: var(--space-6);
  align-items: center;
  justify-content: center;
}

.chart-canvas-wrap {
  width: 100%;
  height: 340px;
}

.chart-stack {
  position: relative;
  width: 100%;
}

.doughnut-center {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  pointer-events: none;
  z-index: 1;
}

.doughnut-center-main {
  font-size: 1.35rem;
  font-weight: 900;
  color: #0f172a;
  line-height: 1.1;
}

.doughnut-center-sub {
  margin-top: 4px;
  font-size: 0.7rem;
  font-weight: 900;
  color: #94a3b8;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.chart-canvas-wrap.is-hidden {
  opacity: 0;
}

.chart-canvas-wrap.chart-canvas-sm {
  width: 100%;
  height: 240px;
}

.chart-canvas {
  width: 100%;
  height: 100%;
}

.skeleton-chart {
  width: 100%;
  height: 340px;
  border-radius: var(--rounded-lg);
  background: linear-gradient(90deg, #f1f5f9, #e2e8f0, #f1f5f9);
  background-size: 200% 100%;
  animation: skeleton-move 1.2s ease-in-out infinite;
}

.skeleton-chart.skeleton-overlay {
  position: absolute;
  inset: 0;
  z-index: 2;
}

@keyframes skeleton-move {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.legend-clean {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.legend-label {
  display: block;
  font-size: 0.85rem;
  font-weight: 600;
  color: #64748b;
}

.legend-val {
  font-size: 1rem;
  font-weight: 800;
  color: #0f172a;
}

.empty-hbar {
  color: #94a3b8;
  font-weight: 700;
  text-align: center;
  padding: 12px 0;
}

.range-note {
  margin-top: var(--space-2);
  font-weight: 900;
  color: #0f172a;
}
</style>
