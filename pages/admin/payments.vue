<template>
  <div class="payments-page">
    <div class="page-header">
      <div>
        <h1>Paiements</h1>
        <p>Choisir une réservation non soldée, payer en avance ou en totalité</p>
      </div>
      <div class="header-actions">
        <button class="btn btn-export btn-sm" :class="{ 'is-loading': exportingPdf }" :disabled="exportingPdf || exportingXls" @click="exportPdf">
          <i class="fas fa-file-pdf"></i> Export PDF
        </button>
        <button class="btn btn-export btn-sm" :class="{ 'is-loading': exportingXls }" :disabled="exportingPdf || exportingXls" @click="exportXls">
          <i class="fas fa-file-excel"></i> Export XLS
        </button>
        <button class="btn btn-primary btn-sm" @click="openAddModal()">
          <i class="fas fa-plus"></i> Nouveau paiement
        </button>
      </div>
    </div>

    <div class="controls card">
      <div class="controls-top">
        <div class="search-wrapper">
          <i class="fas fa-search search-icon"></i>
          <input
            type="text"
            v-model="search"
            placeholder="Rechercher (client, email, référence)..."
            class="search-input-clean"
          />
        </div>
        <button class="btn-icon filters-toggle" :class="{ active: filtersOpen }" title="Filtres" @click="filtersOpen = !filtersOpen">
          <i class="fas fa-filter"></i>
        </button>
      </div>
      <div v-show="!isMobile || filtersOpen" class="filters-panel">
        <select v-model="statusFilter" class="filter-select-clean">
          <option value="">Tous les statuts</option>
          <option value="paid">Payé</option>
          <option value="pending">En attente</option>
          <option value="failed">Échoué</option>
        </select>
        <select v-model="methodFilter" class="filter-select-clean">
          <option value="">Toutes les méthodes</option>
          <option v-for="m in methods" :key="m" :value="m">{{ m }}</option>
        </select>
        <input v-model="dateFrom" type="date" class="filter-input-clean" />
        <input v-model="dateTo" type="date" class="filter-input-clean" />
      </div>
    </div>

    <div ref="exportRef" class="export-scope">
    <div class="stats-grid">
      <div class="stat-card card">
        <div class="stat-icon success"><i class="fas fa-hand-holding-usd"></i></div>
        <div class="stat-info">
          <span class="label">Revenu encaissé</span>
          <span class="value success">
            <span v-if="isLoading" class="skeleton-line skeleton-w-70"></span>
            <template v-else>{{ formatMoney(displayTotalRevenue) }}</template>
          </span>
        </div>
      </div>
      <div class="stat-card card">
        <div class="stat-icon warning"><i class="fas fa-hourglass-half"></i></div>
        <div class="stat-info">
          <span class="label">Reste à encaisser</span>
          <span class="value warning">
            <span v-if="isLoading" class="skeleton-line skeleton-w-70"></span>
            <template v-else>{{ formatMoney(displayTotalRemaining) }}</template>
          </span>
        </div>
      </div>
      <div class="stat-card card">
        <div class="stat-icon info"><i class="fas fa-list-check"></i></div>
        <div class="stat-info">
          <span class="label">Réservations non soldées</span>
          <span class="value info">
            <span v-if="isLoading" class="skeleton-line skeleton-w-30"></span>
            <template v-else>{{ displayUnpaidBookings }}</template>
          </span>
        </div>
      </div>
      <div class="stat-card card">
        <div class="stat-icon primary"><i class="fas fa-exchange-alt"></i></div>
        <div class="stat-info">
          <span class="label">Transactions</span>
          <span class="value">
            <span v-if="isLoading" class="skeleton-line skeleton-w-30"></span>
            <template v-else>{{ displayPaymentsCount }}</template>
          </span>
        </div>
      </div>
    </div>

    <div class="card section-card">
      <div class="section-header" style="display:flex; align-items:center; justify-content:space-between; gap:12px; flex-wrap:wrap;">
        <h2>Réservations à payer</h2>
        <AdminAppTablePagination
          :start="unpaidStartIndex"
          :end="unpaidEndIndex"
          :total="unpaidTotalItems"
          :can-prev="unpaidCanPrev"
          :can-next="unpaidCanNext"
          :disabled="isLoading"
          @prev="unpaidPrevPage"
          @next="unpaidNextPage"
        />
      </div>
      <div v-if="isMobile" class="admin-cards">
        <template v-if="isLoading">
          <div v-for="n in 5" :key="`sk-unpaid-card-${n}`" class="admin-card">
            <div class="admin-card-head">
              <div style="width: 100%;">
                <div class="skeleton-line skeleton-w-60"></div>
                <div style="margin-top: 8px;" class="skeleton-line skeleton-w-40"></div>
              </div>
            </div>
            <div class="admin-card-body">
              <div class="skeleton-line skeleton-w-60"></div>
              <div class="skeleton-line skeleton-w-50"></div>
              <div class="skeleton-line skeleton-w-40"></div>
            </div>
          </div>
        </template>
        <template v-else>
          <div v-for="booking in paginatedUnpaidBookings" :key="booking.id" class="admin-card has-actions">
            <div class="admin-card-head">
              <div>
                <div class="admin-card-title">{{ booking.customer_name }}</div>
                <div class="admin-card-subtitle">{{ getBookingDisplayId(booking) }} • {{ booking.hall_name }} • {{ formatDateRange(booking.start_date, booking.end_date) }}</div>
              </div>
              <div class="admin-card-actions">
                <button class="btn btn-primary btn-sm" title="Payer" @click="openAddModal(booking)">
                  <i class="fas fa-coins"></i>
                </button>
              </div>
            </div>
            <div class="admin-card-body">
              <div class="admin-kv">
                <span class="k">ID</span>
                <span class="v">{{ getBookingDisplayId(booking) }}</span>
              </div>
              <div class="admin-kv">
                <span class="k">Total</span>
                <span class="v">{{ formatMoney(booking.total_price) }}</span>
              </div>
              <div class="admin-kv">
                <span class="k">Déjà payé</span>
                <span class="v">{{ formatMoney(booking.paid_amount) }}</span>
              </div>
              <div class="admin-kv">
                <span class="k">Reste</span>
                <span class="v">{{ formatMoney(booking.remaining_amount) }}</span>
              </div>
            </div>
          </div>
        </template>
        <div v-if="!isLoading && filteredUnpaidBookings.length === 0" class="empty-cell">Toutes les réservations sont soldées</div>
      </div>

      <table v-else class="admin-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Client</th>
            <th>Salle</th>
            <th>Période</th>
            <th>Total</th>
            <th>Déjà payé</th>
            <th>Reste</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          <template v-if="isLoading">
            <tr v-for="n in 5" :key="`sk-unpaid-${n}`">
              <td><div class="skeleton-line skeleton-w-50"></div></td>
              <td>
                <div class="skeleton-lines">
                  <div class="skeleton-line skeleton-w-60"></div>
                  <div class="skeleton-line skeleton-w-40"></div>
                </div>
              </td>
              <td><div class="skeleton-line skeleton-w-50"></div></td>
              <td><div class="skeleton-line skeleton-w-60"></div></td>
              <td><div class="skeleton-line skeleton-w-40"></div></td>
              <td><div class="skeleton-line skeleton-w-40"></div></td>
              <td><div class="skeleton-line skeleton-w-40"></div></td>
              <td><div class="skeleton-line skeleton-w-50"></div></td>
            </tr>
          </template>
          <template v-else>
            <tr v-for="booking in paginatedUnpaidBookings" :key="booking.id">
              <td><code>{{ getBookingDisplayId(booking) }}</code></td>
              <td>
                <div class="customer-name">{{ booking.customer_name }}</div>
                <div class="customer-email">{{ booking.customer_email }}</div>
              </td>
              <td>{{ booking.hall_name }}</td>
              <td>{{ formatDateRange(booking.start_date, booking.end_date) }}</td>
              <td>{{ formatMoney(booking.total_price) }}</td>
              <td>{{ formatMoney(booking.paid_amount) }}</td>
              <td><span class="remain">{{ formatMoney(booking.remaining_amount) }}</span></td>
              <td>
                <button class="btn btn-primary btn-sm" @click="openAddModal(booking)">
                  <i class="fas fa-coins"></i> Payer
                </button>
              </td>
            </tr>
            <tr v-if="filteredUnpaidBookings.length === 0">
              <td colspan="8" class="empty-cell">Toutes les réservations sont soldées</td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>

    <div class="card section-card">
      <div class="section-header" style="display:flex; align-items:center; justify-content:space-between; gap:12px; flex-wrap:wrap;">
        <h2>Historique des paiements</h2>
        <AdminAppTablePagination
          :start="paymentsStartIndex"
          :end="paymentsEndIndex"
          :total="paymentsTotalItems"
          :can-prev="paymentsCanPrev"
          :can-next="paymentsCanNext"
          :disabled="isLoading"
          @prev="paymentsPrevPage"
          @next="paymentsNextPage"
        />
      </div>
      <div v-if="isMobile" class="admin-cards">
        <template v-if="isLoading">
          <div v-for="n in 6" :key="`sk-pay-card-${n}`" class="admin-card">
            <div class="admin-card-head">
              <div style="width: 100%;">
                <div class="skeleton-line skeleton-w-60"></div>
                <div style="margin-top: 8px;" class="skeleton-line skeleton-w-40"></div>
              </div>
            </div>
            <div class="admin-card-body">
              <div class="skeleton-line skeleton-w-60"></div>
              <div class="skeleton-line skeleton-w-40"></div>
              <div class="skeleton-line skeleton-w-50"></div>
            </div>
          </div>
        </template>
        <template v-else>
          <div v-for="payment in paginatedPayments" :key="payment.id" class="admin-card has-actions">
            <div class="admin-card-head">
              <div>
                <div class="admin-card-title">{{ payment.booking_customer_name }}</div>
                <div class="admin-card-subtitle">{{ getPaymentDisplayId(payment) }} • {{ formatDisplayDate(payment.date) }} • {{ formatMoney(payment.amount) }}</div>
              </div>
              <div class="admin-card-actions">
                <div class="actions-dropdown">
                <button class="btn-icon details" title="Détails" @click.stop="toggleActions(payment.id)">
                  <i class="fas fa-ellipsis-vertical"></i>
                </button>
                <div v-if="openActionsId === payment.id" class="actions-menu" @click.stop>
                  <button class="actions-item" @click="viewPayment(payment)">
                    <i class="fas fa-eye"></i> Voir
                  </button>
                  <button class="actions-item danger" @click="confirmDelete(payment)">
                    <i class="fas fa-trash-alt"></i> Supprimer
                  </button>
                </div>
                </div>
              </div>
            </div>

            <div class="admin-card-body">
              <div class="admin-kv">
                <span class="k">ID</span>
                <span class="v">{{ getPaymentDisplayId(payment) }}</span>
              </div>
              <div class="admin-kv">
                <span class="k">Référence</span>
                <span class="v">{{ payment.reference }}</span>
              </div>
              <div class="admin-kv">
                <span class="k">Type</span>
                <span class="v">{{ payment.kind === 'full' ? 'Total' : 'Avance' }}</span>
              </div>
              <div class="admin-kv">
                <span class="k">Méthode</span>
                <span class="v">{{ payment.method }}</span>
              </div>
              <div class="admin-kv">
                <span class="k">Statut</span>
                <span class="v"><span :class="['badge', getBadgeClass(payment.status)]">{{ translateStatus(payment.status) }}</span></span>
              </div>
            </div>
          </div>
        </template>
        <div v-if="!isLoading && filteredPayments.length === 0" class="empty-cell">Aucun paiement enregistré</div>
      </div>

      <table v-else class="admin-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Date</th>
            <th>Client</th>
            <th>Référence</th>
            <th>Type</th>
            <th>Montant</th>
            <th>Méthode</th>
            <th>Statut</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <template v-if="isLoading">
            <tr v-for="n in 6" :key="`sk-payments-${n}`">
              <td><div class="skeleton-line skeleton-w-50"></div></td>
              <td><div class="skeleton-line skeleton-w-40"></div></td>
              <td><div class="skeleton-line skeleton-w-50"></div></td>
              <td><div class="skeleton-line skeleton-w-60"></div></td>
              <td><div class="skeleton-line skeleton-w-30"></div></td>
              <td><div class="skeleton-line skeleton-w-40"></div></td>
              <td><div class="skeleton-line skeleton-w-30"></div></td>
              <td><div class="skeleton-line skeleton-w-30"></div></td>
              <td><div class="skeleton-line skeleton-w-60"></div></td>
            </tr>
          </template>
          <template v-else>
            <tr v-for="payment in paginatedPayments" :key="payment.id">
              <td><code>{{ getPaymentDisplayId(payment) }}</code></td>
              <td>{{ formatDisplayDate(payment.date) }}</td>
              <td>{{ payment.booking_customer_name }}</td>
              <td><code>{{ payment.reference }}</code></td>
              <td>{{ payment.kind === 'full' ? 'Total' : 'Avance' }}</td>
              <td>{{ formatMoney(payment.amount) }}</td>
              <td>{{ payment.method }}</td>
              <td><span :class="['badge', getBadgeClass(payment.status)]">{{ translateStatus(payment.status) }}</span></td>
              <td class="actions-cell">
                <div class="actions-dropdown">
                  <button class="btn-icon details" title="Détails" @click.stop="toggleActions(payment.id)">
                    <i class="fas fa-ellipsis-vertical"></i>
                  </button>
                  <div v-if="openActionsId === payment.id" class="actions-menu" @click.stop>
                    <button class="actions-item" @click="viewPayment(payment)">
                      <i class="fas fa-eye"></i> Voir
                    </button>
                    <button class="actions-item danger" @click="confirmDelete(payment)">
                      <i class="fas fa-trash-alt"></i> Supprimer
                    </button>
                  </div>
                </div>
              </td>
            </tr>
            <tr v-if="filteredPayments.length === 0">
              <td colspan="9" class="empty-cell">Aucun paiement enregistré</td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>
    </div>

    <AdminAppModal v-model="showFormModal" title="Enregistrer un paiement" width="560px">
      <form class="admin-form" @submit.prevent="savePayment">
        <div class="form-group">
          <label class="form-label">Réservation</label>
          <select v-model="form.booking" class="form-select" required @change="onBookingChange">
            <option v-for="b in unpaidBookings" :key="b.id" :value="b.id">
              {{ b.customer_name }} - {{ b.hall_name }} (reste: {{ formatMoney(b.remaining_amount) }})
            </option>
          </select>
        </div>

        <div v-if="selectedBookingForForm" class="booking-summary">
          <div><strong>Total:</strong> {{ formatMoney(selectedBookingForForm.total_price) }}</div>
          <div><strong>Déjà payé:</strong> {{ formatMoney(selectedBookingForForm.paid_amount) }}</div>
          <div><strong>Reste:</strong> {{ formatMoney(selectedBookingForForm.remaining_amount) }}</div>
        </div>

        <div class="form-grid">
          <div class="form-group">
            <label class="form-label">Type de paiement</label>
            <select v-model="form.kind" class="form-select" @change="onKindChange">
              <option value="advance">Avance</option>
              <option value="full">Paiement total</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Montant (Fbu)</label>
            <input v-model="amountInput" inputmode="numeric" type="text" class="form-input" placeholder="0" required />
          </div>
        </div>

        <div class="form-grid">
          <div class="form-group">
            <label class="form-label">Date</label>
            <input v-model="form.date" type="date" class="form-input" required />
          </div>
          <div class="form-group">
            <label class="form-label">Méthode</label>
            <select v-model="form.method" class="form-select" required>
              <option value="Virement">Virement</option>
              <option value="Espèces">Espèces</option>
              <option value="Carte">Carte</option>
              <option value="Mobile Money">Mobile Money</option>
            </select>
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">Référence</label>
          <input v-model="form.reference" type="text" class="form-input" required />
        </div>
      </form>
      <template #footer>
        <button class="btn btn-outline" @click="showFormModal = false">Annuler</button>
        <button class="btn btn-primary" :class="{ 'is-loading': savingPayment }" :disabled="savingPayment" @click="savePayment">
          Enregistrer
        </button>
      </template>
    </AdminAppModal>

    <AdminAppModal v-model="showViewModal" title="Détails du paiement" width="420px">
      <div v-if="selectedPayment" class="view-details">
        <div class="detail-item"><span class="detail-label">ID</span><span class="detail-val">{{ getPaymentDisplayId(selectedPayment) }}</span></div>
        <div class="detail-item"><span class="detail-label">Client</span><span class="detail-val">{{ selectedPayment.booking_customer_name }}</span></div>
        <div class="detail-item"><span class="detail-label">Réservation</span><span class="detail-val">{{ selectedPayment.booking_hall_name }}</span></div>
        <div class="detail-item"><span class="detail-label">Période</span><span class="detail-val">{{ formatDateRange(selectedPayment.booking_start_date, selectedPayment.booking_end_date) }}</span></div>
        <div class="detail-item"><span class="detail-label">Type</span><span class="detail-val">{{ selectedPayment.kind === 'full' ? 'Paiement total' : 'Avance' }}</span></div>
        <div class="detail-item"><span class="detail-label">Montant</span><span class="detail-val">{{ formatMoney(selectedPayment.amount) }}</span></div>
        <div class="detail-item"><span class="detail-label">Reste après paiement</span><span class="detail-val">{{ formatMoney(selectedPayment.booking_remaining_amount) }}</span></div>
      </div>
      <template #footer>
        <button class="btn btn-primary" @click="showViewModal = false">Fermer</button>
      </template>
    </AdminAppModal>

    <AdminAppModal v-model="showDeleteModal" title="Confirmer la suppression" width="400px">
      <p>Supprimer le paiement <strong>{{ selectedPayment?.reference }}</strong> ?</p>
      <template #footer>
        <button class="btn btn-outline" @click="showDeleteModal = false">Annuler</button>
        <button class="btn btn-danger" :class="{ 'is-loading': deletingPayment }" :disabled="deletingPayment" @click="deletePayment">
          Supprimer
        </button>
      </template>
    </AdminAppModal>
  </div>
</template>

<script setup>
import { notify } from '~/composables/useNotification'
import { api } from '~/composables/useApi'
import { useMoney } from '~/composables/useMoney'
import { usePagination } from '~/composables/usePagination'
import { useDateFormat } from '~/composables/useDateFormat'
import { useDisplayIds } from '~/composables/useDisplayIds'

definePageMeta({ layout: 'admin' })
const route = useRoute()
const { formatMoney, moneyInputModel } = useMoney()
const { formatDateRange, formatDisplayDate } = useDateFormat()
const { buildMonthlySequenceMap } = useDisplayIds()

const payments = ref([])
const bookings = ref([])
const exportRef = ref(null)
const exportingPdf = ref(false)
const exportingXls = ref(false)
const search = ref('')
const statusFilter = ref('')
const methodFilter = ref('')
const dateFrom = ref('')
const dateTo = ref('')
const loadingPayments = ref(false)
const loadingBookingsData = ref(false)
const isMobile = ref(false)
const filtersOpen = ref(false)
const openActionsId = ref(null)
const savingPayment = ref(false)
const deletingPayment = ref(false)

const toggleActions = (id) => {
  openActionsId.value = openActionsId.value === id ? null : id
}

const closeActions = () => {
  openActionsId.value = null
}

const isLoading = computed(() => loadingPayments.value || loadingBookingsData.value)

const exportXls = async () => {
  if (!exportRef.value) return
  exportingXls.value = true
  await nextTick()
  const html = `<!doctype html><html><head><meta charset="utf-8"></head><body>${exportRef.value.innerHTML}</body></html>`
  const blob = new Blob([html], { type: 'application/vnd.ms-excel' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'payments.xls'
  a.click()
  URL.revokeObjectURL(url)
  setTimeout(() => {
    exportingXls.value = false
  }, 350)
}

const exportPdf = async () => {
  if (!exportRef.value) return
  exportingPdf.value = true
  await nextTick()
  const win = window.open('', '_blank')
  if (!win) {
    exportingPdf.value = false
    return
  }
  win.document.write(`<!doctype html><html><head><meta charset="utf-8"><title>Paiements</title><style>
  body{font-family:Arial, sans-serif; padding:20px}
  table{width:100%; border-collapse:collapse; margin-bottom:16px}
  th,td{border:1px solid #e2e8f0; padding:8px; text-align:left; font-size:12px}
  th{background:#f8fafc}
  </style></head><body><h2>Paiements</h2>${exportRef.value.innerHTML}</body></html>`)
  win.document.close()
  win.focus()
  win.print()
  win.close()
  setTimeout(() => {
    exportingPdf.value = false
  }, 350)
}
const showFormModal = ref(false)
const showViewModal = ref(false)
const showDeleteModal = ref(false)
const selectedPayment = ref(null)

const form = ref({
  booking: null,
  date: new Date().toISOString().split('T')[0],
  reference: '',
  amount: 0,
  method: 'Virement',
  kind: 'advance',
  status: 'paid'
})
const amountInput = moneyInputModel(form, 'amount')

const toNumber = (v) => Number(v || 0)
const unpaidBookings = computed(() => bookings.value.filter(b => toNumber(b.remaining_amount) > 0 && b.status !== 'cancelled'))
const filteredUnpaidBookings = computed(() => {
  const q = search.value.toLowerCase().trim()
  return unpaidBookings.value.filter((b) => {
    const matchesSearch = q === '' ||
      String(b.customer_name || '').toLowerCase().includes(q) ||
      String(b.customer_email || '').toLowerCase().includes(q) ||
      String(b.hall_name || '').toLowerCase().includes(q)
    return matchesSearch
  })
})

const bookingDisplayIds = computed(() => buildMonthlySequenceMap(bookings.value, 'LBR', booking => booking.start_date))
const getBookingDisplayId = (booking) => bookingDisplayIds.value.get(booking?.id) || 'LBR00000001'

const {
  paginatedItems: paginatedUnpaidBookings,
  totalItems: unpaidTotalItems,
  startIndex: unpaidStartIndex,
  endIndex: unpaidEndIndex,
  canPrev: unpaidCanPrev,
  canNext: unpaidCanNext,
  prevPage: unpaidPrevPage,
  nextPage: unpaidNextPage,
} = usePagination(filteredUnpaidBookings, 50)

const selectedBookingForForm = computed(() => unpaidBookings.value.find(b => b.id === form.value.booking) || null)
const totalRevenue = computed(() => payments.value.filter(p => p.status === 'paid').reduce((a, p) => a + toNumber(p.amount), 0))
const totalRemaining = computed(() => unpaidBookings.value.reduce((a, b) => a + toNumber(b.remaining_amount), 0))
const methods = computed(() => Array.from(new Set((payments.value || []).map(p => p.method).filter(Boolean))).sort())

const displayTotalRevenue = ref(0)
const displayTotalRemaining = ref(0)
const displayUnpaidBookings = ref(0)
const displayPaymentsCount = ref(0)

const rafMap = new Map()
const animateCounter = (outRef, toValue) => {
  if (typeof requestAnimationFrame === 'undefined' || typeof cancelAnimationFrame === 'undefined') {
    outRef.value = Math.round(Number(toValue || 0))
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
    outRef.value = Math.round(current)
    if (p < 1) rafMap.set(outRef, requestAnimationFrame(step))
  }

  rafMap.set(outRef, requestAnimationFrame(step))
}

watch(totalRevenue, (v) => animateCounter(displayTotalRevenue, v), { immediate: true })
watch(totalRemaining, (v) => animateCounter(displayTotalRemaining, v), { immediate: true })
watch(() => unpaidBookings.value.length, (v) => animateCounter(displayUnpaidBookings, v), { immediate: true })
watch(() => payments.value.length, (v) => animateCounter(displayPaymentsCount, v), { immediate: true })

onBeforeUnmount(() => {
  for (const id of rafMap.values()) cancelAnimationFrame(id)
})

const filteredPayments = computed(() => {
  const q = search.value.toLowerCase().trim()
  return (payments.value || []).filter((p) => {
    const matchesSearch = q === '' ||
      String(p.booking_customer_name || '').toLowerCase().includes(q) ||
      String(p.reference || '').toLowerCase().includes(q)
    const matchesStatus = statusFilter.value === '' || p.status === statusFilter.value
    const matchesMethod = methodFilter.value === '' || p.method === methodFilter.value
    const date = p.date ? new Date(p.date) : null
    const fromOk = !dateFrom.value || (date && date >= new Date(dateFrom.value))
    const toOk = !dateTo.value || (date && date <= new Date(dateTo.value))
    return matchesSearch && matchesStatus && matchesMethod && fromOk && toOk
  })
})

const paymentDisplayIds = computed(() => buildMonthlySequenceMap(payments.value, 'LBP', payment => payment.date))
const getPaymentDisplayId = (payment) => paymentDisplayIds.value.get(payment?.id) || 'LBP00000001'

const {
  paginatedItems: paginatedPayments,
  totalItems: paymentsTotalItems,
  startIndex: paymentsStartIndex,
  endIndex: paymentsEndIndex,
  canPrev: paymentsCanPrev,
  canNext: paymentsCanNext,
  prevPage: paymentsPrevPage,
  nextPage: paymentsNextPage,
} = usePagination(filteredPayments, 50)

const fetchPayments = async () => {
  loadingPayments.value = true
  try {
    const { data } = await api.get('payments/')
    payments.value = data
  } catch {
    notify('Erreur lors du chargement des paiements', 'danger')
  } finally {
    loadingPayments.value = false
  }
}

const fetchBookings = async () => {
  loadingBookingsData.value = true
  try {
    const { data } = await api.get('bookings/')
    bookings.value = data
  } catch {
    notify('Erreur lors du chargement des réservations', 'danger')
  } finally {
    loadingBookingsData.value = false
  }
}

const resetForm = () => {
  form.value = {
    booking: unpaidBookings.value[0]?.id || null,
    date: new Date().toISOString().split('T')[0],
    reference: 'PAY-' + Math.floor(1000 + Math.random() * 9000),
    amount: 0,
    method: 'Virement',
    kind: 'advance',
    status: 'paid'
  }
}

const onKindChange = () => {
  if (!selectedBookingForForm.value) return
  if (form.value.kind === 'full') {
    form.value.amount = toNumber(selectedBookingForForm.value.remaining_amount)
  }
}

const onBookingChange = () => {
  if (!selectedBookingForForm.value) return
  if (form.value.kind === 'full') {
    form.value.amount = toNumber(selectedBookingForForm.value.remaining_amount)
  } else if (form.value.amount <= 0) {
    form.value.amount = Math.min(100000, toNumber(selectedBookingForForm.value.remaining_amount))
  }
}

const openAddModal = (booking = null) => {
  resetForm()
  if (booking?.id) {
    form.value.booking = booking.id
  } else if (route.query.booking) {
    form.value.booking = Number(route.query.booking)
  }
  onBookingChange()
  showFormModal.value = true
}

const savePayment = async () => {
  if (savingPayment.value) return
  if (!selectedBookingForForm.value) {
    notify('Sélectionnez une réservation', 'warning')
    return
  }
  const remaining = toNumber(selectedBookingForForm.value.remaining_amount)
  if (form.value.amount <= 0) {
    notify('Montant invalide', 'warning')
    return
  }
  if (form.value.amount > remaining) {
    notify('Le montant dépasse le reste à payer', 'warning')
    return
  }
  savingPayment.value = true
  try {
    await api.post('payments/', form.value)
    notify('Paiement enregistré avec succès', 'success')
    showFormModal.value = false
    await Promise.all([fetchPayments(), fetchBookings()])
  } catch {
    notify('Erreur lors de l\'enregistrement du paiement', 'danger')
  } finally {
    savingPayment.value = false
  }
}

const viewPayment = (payment) => {
  closeActions()
  selectedPayment.value = payment
  showViewModal.value = true
}

const confirmDelete = (payment) => {
  closeActions()
  selectedPayment.value = payment
  showDeleteModal.value = true
}

const deletePayment = async () => {
  if (deletingPayment.value || !selectedPayment.value?.id) return
  deletingPayment.value = true
  try {
    await api.delete(`payments/${selectedPayment.value.id}/`)
    notify('Paiement supprimé', 'danger')
    showDeleteModal.value = false
    await Promise.all([fetchPayments(), fetchBookings()])
  } catch {
    notify('Erreur lors de la suppression', 'danger')
  } finally {
    deletingPayment.value = false
  }
}

const translateStatus = (status) => ({ paid: 'Complété', pending: 'En attente', failed: 'Échoué' }[status] || status)
const getBadgeClass = (status) => ({ paid: 'badge-success', pending: 'badge-warning', failed: 'badge-danger' }[status] || '')

onMounted(async () => {
  await Promise.all([fetchPayments(), fetchBookings()])
  if (route.query.booking) openAddModal()
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

    const onDocClick = () => { openActionsId.value = null }
    document.addEventListener('click', onDocClick)
    onBeforeUnmount(() => document.removeEventListener('click', onDocClick))
  }
})
</script>

<style scoped>
.payments-page { padding: 0; }
.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: var(--space-8); gap: var(--space-4); flex-wrap: wrap; }
.page-header h1 { font-size: 1.75rem; font-weight: 800; margin: 0; color: #0f172a; }
.page-header p { color: #64748b; margin-top: .35rem; }
.header-actions { display: inline-flex; gap: .5rem; flex-wrap: wrap; align-items: center; justify-content: flex-end; }

.controls { display: flex; gap: var(--space-4); margin-bottom: var(--space-8); padding: var(--space-4) var(--space-6); align-items: center; flex-wrap: wrap; }
.controls-top { width: 100%; display: flex; gap: var(--space-3); align-items: center; }
.filters-panel { width: 100%; display: flex; gap: var(--space-4); flex-wrap: wrap; align-items: center; }
.filters-toggle { display: none; width: 42px; height: 42px; border: 1px solid #e2e8f0; background: #f8fafc; color: #475569; }
.filters-toggle.active { background: rgba(212, 175, 55, .18); border-color: rgba(212, 175, 55, .35); color: #0f172a; }
.filters-panel .filter-select-clean, .filters-panel .filter-input-clean { flex: 1 1 190px; }
.search-wrapper { flex: 1 1 320px; position: relative; }
.search-icon { position: absolute; left: 1rem; top: 50%; transform: translateY(-50%); color: #94a3b8; font-size: 0.9rem; }
.search-input-clean { width: 100%; padding: 0.625rem 1rem 0.625rem 2.5rem; border: 1px solid #e2e8f0; border-radius: var(--rounded-md); font-size: 0.9rem; background: #f8fafc; transition: var(--transition-fast); }
.search-input-clean:focus { background: white; border-color: var(--accent); box-shadow: 0 0 0 3px rgba(212, 175, 55, 0.1); }
.filter-select-clean { padding: 0.625rem 2rem 0.625rem 1rem; border: 1px solid #e2e8f0; border-radius: var(--rounded-md); font-size: 0.9rem; background: #f8fafc; color: #475569; font-weight: 600; cursor: pointer; }
.filter-input-clean { padding: 0.625rem 1rem; border: 1px solid #e2e8f0; border-radius: var(--rounded-md); font-size: 0.9rem; background: #f8fafc; color: #475569; font-weight: 600; transition: var(--transition-fast); }
.filter-input-clean:focus { background: white; border-color: var(--accent); box-shadow: 0 0 0 3px rgba(212, 175, 55, 0.1); }

.stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: var(--space-5); margin-bottom: var(--space-8); }
.stat-card { display: flex; align-items: center; gap: var(--space-4); padding: var(--space-5); }
.stat-icon { width: 44px; height: 44px; border-radius: 10px; display: flex; align-items: center; justify-content: center; }
.stat-icon.success { background: #ecfdf3; color: #16a34a; }
.stat-icon.warning { background: #fffbeb; color: #d97706; }
.stat-icon.info { background: #eff6ff; color: #2563eb; }
.stat-icon.primary { background: #eef2ff; color: #4338ca; }
.label { display: block; color: #94a3b8; font-size: .72rem; text-transform: uppercase; font-weight: 700; letter-spacing: .05em; }
.value { font-size: 1.2rem; font-weight: 800; color: #0f172a; }
.value.success { color: #16a34a; }
.value.warning { color: #d97706; }
.value.info { color: #2563eb; }
.section-card { margin-bottom: var(--space-8); }
.section-header { margin-bottom: var(--space-4); }
.section-header h2 { font-size: 1rem; font-weight: 800; color: #1e293b; }
.customer-name { font-weight: 700; color: #0f172a; }
.customer-email { font-size: .8rem; color: #94a3b8; }
.remain { color: #b45309; font-weight: 800; }
.empty-cell { text-align: center; color: #94a3b8; font-weight: 600; padding: 1rem; }
.booking-summary { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: .85rem 1rem; display: grid; gap: .3rem; margin-bottom: .25rem; }
.btn-sm { padding: .45rem .75rem; font-size: .78rem; }
.btn-icon { width: 32px; height: 32px; background: #f8fafc; color: #64748b; }
.view-details { display: grid; gap: .7rem; }
.detail-item { display: flex; justify-content: space-between; border-bottom: 1px solid #f1f5f9; padding-bottom: .45rem; }
.detail-label { color: #64748b; font-weight: 600; }
.detail-val { color: #0f172a; font-weight: 700; text-align: right; }

.actions-cell { width: 1%; white-space: nowrap; }
.actions-dropdown { position: relative; display: inline-flex; }
.actions-menu { position: absolute; top: calc(100% + 8px); right: 0; min-width: 180px; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; box-shadow: 0 14px 35px rgba(15, 23, 42, 0.12); padding: 6px; z-index: 30; }
.actions-item { width: 100%; display: flex; align-items: center; gap: 10px; padding: 10px 12px; border-radius: 10px; color: #334155; font-weight: 700; font-size: 0.9rem; text-align: left; }
.actions-item:hover { background: #f8fafc; color: #0f172a; }
.actions-item.danger { color: #dc2626; }
.actions-item.danger:hover { background: #fef2f2; color: #b91c1c; }

@media (max-width: 992px) {
  .filters-toggle { display: inline-flex; align-items: center; justify-content: center; }
  .filters-panel { gap: var(--space-3); }
}
</style>
