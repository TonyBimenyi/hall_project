<template>
  <div class="admin-reports">
    <div class="header-actions">
      <div>
        <h1>Rapports et Statistiques</h1>
        <p class="subtitle">Analyse des performances et de l'activité</p>
      </div>
      <div class="filters-group">
        <select class="filter-select-clean">
          <option>Ce mois-ci</option>
          <option>Dernier trimestre</option>
          <option>Année 2026</option>
        </select>
        <button class="btn btn-export btn-sm" @click="exportPdf">
          <i class="fas fa-file-pdf"></i> Export PDF
        </button>
        <button class="btn btn-export btn-sm" @click="exportXls">
          <i class="fas fa-file-excel"></i> Export XLS
        </button>
      </div>
    </div>

    <div class="summary-cards mb-8">
      <div class="summary-card card">
        <div class="summary-icon success"><i class="fas fa-wallet"></i></div>
        <div>
          <span class="label">Revenu Net (Mai)</span>
          <span class="value success">+{{ stats.monthly_revenue.toLocaleString() }} Fbu</span>
        </div>
      </div>
      <div class="summary-card card">
        <div class="summary-icon danger"><i class="fas fa-arrow-trend-down"></i></div>
        <div>
          <span class="label">Dépenses Totales</span>
          <span class="value danger">-{{ stats.monthly_expenses.toLocaleString() }} Fbu</span>
        </div>
      </div>
      <div class="summary-card card">
        <div class="summary-icon primary"><i class="fas fa-percentage"></i></div>
        <div>
          <span class="label">Marge Bénéficiaire</span>
          <span class="value primary">{{ profitMargin }}%</span>
        </div>
      </div>
      <div class="summary-card card">
        <div class="summary-icon info"><i class="fas fa-smile"></i></div>
        <div>
          <span class="label">Satisfaction Client</span>
          <span class="value info">4.8/5</span>
        </div>
      </div>
    </div>

    <div class="summary-cards mb-8">
      <div class="summary-card card">
        <div class="summary-icon primary"><i class="fas fa-calendar-check"></i></div>
        <div>
          <span class="label">Réservations (Total)</span>
          <span class="value">{{ bookingCounts.total }}</span>
        </div>
      </div>
      <div class="summary-card card">
        <div class="summary-icon warning"><i class="fas fa-hourglass-half"></i></div>
        <div>
          <span class="label">En attente</span>
          <span class="value warning">{{ bookingCounts.pending }}</span>
        </div>
      </div>
      <div class="summary-card card">
        <div class="summary-icon info"><i class="fas fa-circle-check"></i></div>
        <div>
          <span class="label">Confirmées</span>
          <span class="value info">{{ bookingCounts.confirmed }}</span>
        </div>
      </div>
      <div class="summary-card card">
        <div class="summary-icon success"><i class="fas fa-coins"></i></div>
        <div>
          <span class="label">Payées</span>
          <span class="value success">{{ bookingCounts.paid }}</span>
        </div>
      </div>
    </div>

    <div class="charts-grid">
      <div class="chart-card card">
        <div class="card-header">
          <span>Revenus vs Dépenses</span>
        </div>
        <div class="chart-content-clean">
          <div class="bars-container">
            <div class="bar-group" v-for="bar in revenueBars" :key="bar.label">
              <div class="bar-clean" :class="bar.variant" :style="{ height: bar.height + '%' }">
                <div class="bar-tooltip">{{ bar.formatted }}</div>
              </div>
              <span class="bar-label">{{ bar.label }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="chart-card card">
        <div class="card-header">
          <span>Taux d'Occupation</span>
        </div>
        <div class="chart-content-clean pie-layout">
          <div class="pie-sim-clean" :style="{ background: occupationGradient }">
            <div class="pie-inner">{{ totalOccupation }}%</div>
          </div>
          <div class="legend-clean">
            <div class="legend-item" v-for="item in occupationLegend" :key="item.type">
              <span class="dot" :style="{ background: item.color }"></span>
              <div class="legend-info">
                <span class="legend-label">{{ item.type }}</span>
                <span class="legend-val">{{ item.percentage }}%</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="static-info">
      <p><i class="fas fa-info-circle"></i> Affichage de données dynamiques (Backend Django)</p>
    </div>
  </div>
</template>

<script setup>
import { api } from '~/composables/useApi'

definePageMeta({ layout: 'admin' })

const stats = ref({
  monthly_revenue: 0,
  monthly_expenses: 0,
  occupation_data: []
})
const bookings = ref([])
const payments = ref([])

const formatMoney = (v) => `${Number(v || 0).toLocaleString()} Fbu`

const revenueBars = computed(() => {
  const revenue = Number(stats.value.monthly_revenue || 0)
  const expenses = Number(stats.value.monthly_expenses || 0)
  const max = Math.max(revenue, expenses, 1)
  return [
    {
      label: 'Revenus',
      height: Math.round((revenue / max) * 100),
      formatted: formatMoney(revenue),
      variant: 'revenue'
    },
    {
      label: 'Dépenses',
      height: Math.round((expenses / max) * 100),
      formatted: formatMoney(expenses),
      variant: 'expense'
    }
  ]
})

const occupationLegend = computed(() => {
  const colors = ['#0f172a', '#22c55e', '#f59e0b', '#0ea5e9', '#ef4444', '#6366f1']
  const items = (stats.value.occupation_data || [])
    .map((i) => ({ type: i.type, percentage: Number(i.percentage || 0) }))
    .filter((i) => i.percentage > 0)
  return items.map((item, idx) => ({ ...item, color: colors[idx % colors.length] }))
})

const occupationGradient = computed(() => {
  const items = occupationLegend.value
  if (items.length === 0) return 'conic-gradient(#e2e8f0 0% 100%)'

  let cursor = 0
  const stops = items.map((item, idx) => {
    const start = cursor
    const end = cursor + item.percentage
    cursor = end
    return `${item.color} ${start}% ${end}%`
  })
  const endFill = cursor < 100 ? `, #e2e8f0 ${cursor}% 100%` : ''
  return `conic-gradient(${stops.join(', ')}${endFill})`
})

const exportXls = () => {
  const rows = [
    ['Revenu Net (Mois)', String(stats.value.monthly_revenue || 0)],
    ['Dépenses Totales (Mois)', String(stats.value.monthly_expenses || 0)],
    ['Marge Bénéficiaire (%)', String(profitMargin.value || 0)],
    ['Occupation totale (%)', String(totalOccupation.value || 0)],
    ['Réservations (Total)', String(bookingCounts.value.total)],
    ['Réservations (En attente)', String(bookingCounts.value.pending)],
    ['Réservations (Confirmées)', String(bookingCounts.value.confirmed)],
    ['Réservations (Payées)', String(bookingCounts.value.paid)],
    ['Réservations (Annulées)', String(bookingCounts.value.cancelled)],
    ['Paiements (Total)', String(payments.value.length)],
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
}

const exportPdf = () => {
  const rows = [
    ['Revenu Net (Mois)', `${Number(stats.value.monthly_revenue || 0).toLocaleString()} Fbu`],
    ['Dépenses Totales (Mois)', `${Number(stats.value.monthly_expenses || 0).toLocaleString()} Fbu`],
    ['Marge Bénéficiaire', `${profitMargin.value || 0}%`],
    ['Occupation totale', `${totalOccupation.value || 0}%`],
    ['Réservations (Total)', String(bookingCounts.value.total)],
    ['En attente', String(bookingCounts.value.pending)],
    ['Confirmées', String(bookingCounts.value.confirmed)],
    ['Payées', String(bookingCounts.value.paid)],
    ['Annulées', String(bookingCounts.value.cancelled)],
    ['Paiements (Total)', String(payments.value.length)],
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
  if (!win) return
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
}

const fetchStats = async () => {
  try {
    const response = await api.get('summary/')
    stats.value = response.data
  } catch (error) {
    console.error('Error fetching stats:', error)
  }
}

const fetchBookings = async () => {
  try {
    const { data } = await api.get('bookings/')
    bookings.value = data
  } catch (error) {
    bookings.value = []
  }
}

const fetchPayments = async () => {
  try {
    const { data } = await api.get('payments/')
    payments.value = data
  } catch (error) {
    payments.value = []
  }
}

onMounted(() => {
  fetchStats()
  fetchBookings()
  fetchPayments()
})

const bookingCounts = computed(() => {
  const counts = { total: 0, pending: 0, confirmed: 0, paid: 0, cancelled: 0 }
  for (const b of bookings.value || []) {
    counts.total += 1
    if (b.status === 'pending') counts.pending += 1
    if (b.status === 'confirmed') counts.confirmed += 1
    if (b.status === 'paid') counts.paid += 1
    if (b.status === 'cancelled') counts.cancelled += 1
  }
  return counts
})

const profitMargin = computed(() => {
  if (stats.value.monthly_revenue === 0) return 0
  const margin = ((stats.value.monthly_revenue - stats.value.monthly_expenses) / stats.value.monthly_revenue) * 100
  return Math.max(0, margin.toFixed(1))
})

const totalOccupation = computed(() => {
  const total = (stats.value.occupation_data || []).reduce((acc, curr) => acc + Number(curr.percentage || 0), 0)
  return Math.min(100, Math.max(0, total)).toFixed(0)
})
</script>

<style scoped>
.admin-reports {
  padding: 0;
}

.header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-10);
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

.filters-group {
  display: flex;
  gap: var(--space-3);
  align-items: center;
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
  align-items: flex-end;
  justify-content: center;
}

.bars-container {
  width: 100%;
  height: 250px;
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  padding: 0 var(--space-4);
}

.bar-group {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-3);
}

.bar-clean {
  width: 32px;
  background: #f1f5f9;
  border-radius: 6px;
  position: relative;
  transition: var(--transition-all);
}

.bar-clean.revenue {
  background: linear-gradient(180deg, #22c55e, #86efac);
}

.bar-clean.expense {
  background: linear-gradient(180deg, #ef4444, #fca5a5);
}

.bar-clean:hover {
  background: #0f172a;
}

.bar-tooltip {
  position: absolute;
  top: -35px;
  left: 50%;
  transform: translateX(-50%) translateY(10px);
  background: #0f172a;
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.7rem;
  font-weight: 700;
  opacity: 0;
  pointer-events: none;
  transition: var(--transition-fast);
}

.bar-clean:hover .bar-tooltip {
  opacity: 1;
  transform: translateX(-50%) translateY(0);
}

.bar-label {
  font-size: 0.75rem;
  font-weight: 700;
  color: #94a3b8;
}

.pie-layout {
  align-items: center;
  gap: var(--space-10);
}

.pie-sim-clean {
  width: 180px;
  height: 180px;
  border-radius: 50%;
  background: conic-gradient(#e2e8f0 0% 100%);
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.pie-inner {
  width: 120px;
  height: 120px;
  background: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  font-weight: 800;
  color: #0f172a;
  box-shadow: inset 0 2px 10px rgba(0,0,0,0.05);
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

.static-info {
  margin-top: var(--space-12);
  color: #cbd5e1;
  font-size: 0.85rem;
  text-align: center;
  font-weight: 600;
}
</style>
