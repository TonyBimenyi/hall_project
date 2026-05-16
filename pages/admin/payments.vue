<template>
  <div class="payments-page">
    <div class="page-header">
      <div>
        <h1>Paiements</h1>
        <p>Choisir une réservation non soldée, payer en avance ou en totalité</p>
      </div>
      <div class="header-actions">
        <button class="btn btn-export btn-sm" @click="exportPdf">
          <i class="fas fa-file-pdf"></i> Export PDF
        </button>
        <button class="btn btn-export btn-sm" @click="exportXls">
          <i class="fas fa-file-excel"></i> Export XLS
        </button>
        <button class="btn btn-primary" @click="openAddModal()">
          <i class="fas fa-plus"></i> Nouveau paiement
        </button>
      </div>
    </div>

    <div class="controls card">
      <div class="search-wrapper">
        <i class="fas fa-search search-icon"></i>
        <input
          type="text"
          v-model="search"
          placeholder="Rechercher (client, email, référence)..."
          class="search-input-clean"
        />
      </div>
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

    <div ref="exportRef" class="export-scope">
    <div class="stats-grid">
      <div class="stat-card card">
        <div class="stat-icon success"><i class="fas fa-hand-holding-usd"></i></div>
        <div class="stat-info">
          <span class="label">Revenu encaissé</span>
          <span class="value success">{{ totalRevenue.toLocaleString() }} Fbu</span>
        </div>
      </div>
      <div class="stat-card card">
        <div class="stat-icon warning"><i class="fas fa-hourglass-half"></i></div>
        <div class="stat-info">
          <span class="label">Reste à encaisser</span>
          <span class="value warning">{{ totalRemaining.toLocaleString() }} Fbu</span>
        </div>
      </div>
      <div class="stat-card card">
        <div class="stat-icon info"><i class="fas fa-list-check"></i></div>
        <div class="stat-info">
          <span class="label">Réservations non soldées</span>
          <span class="value info">{{ unpaidBookings.length }}</span>
        </div>
      </div>
      <div class="stat-card card">
        <div class="stat-icon primary"><i class="fas fa-exchange-alt"></i></div>
        <div class="stat-info">
          <span class="label">Transactions</span>
          <span class="value">{{ payments.length }}</span>
        </div>
      </div>
    </div>

    <div class="card section-card">
      <div class="section-header">
        <h2>Réservations à payer</h2>
      </div>
      <table class="admin-table">
        <thead>
          <tr>
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
          <tr v-for="booking in filteredUnpaidBookings" :key="booking.id">
            <td>
              <div class="customer-name">{{ booking.customer_name }}</div>
              <div class="customer-email">{{ booking.customer_email }}</div>
            </td>
            <td>{{ booking.hall_name }}</td>
            <td>{{ booking.start_date }} → {{ booking.end_date }}</td>
            <td>{{ toNumber(booking.total_price).toLocaleString() }} Fbu</td>
            <td>{{ toNumber(booking.paid_amount).toLocaleString() }} Fbu</td>
            <td><span class="remain">{{ toNumber(booking.remaining_amount).toLocaleString() }} Fbu</span></td>
            <td>
              <button class="btn btn-primary btn-sm" @click="openAddModal(booking)">
                <i class="fas fa-coins"></i> Payer
              </button>
            </td>
          </tr>
          <tr v-if="unpaidBookings.length === 0">
            <td colspan="7" class="empty-cell">Toutes les réservations sont soldées</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="card section-card">
      <div class="section-header">
        <h2>Historique des paiements</h2>
      </div>
      <table class="admin-table">
        <thead>
          <tr>
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
          <tr v-for="payment in filteredPayments" :key="payment.id">
            <td>{{ payment.date }}</td>
            <td>{{ payment.booking_customer_name }}</td>
            <td><code>{{ payment.reference }}</code></td>
            <td>{{ payment.kind === 'full' ? 'Total' : 'Avance' }}</td>
            <td>{{ toNumber(payment.amount).toLocaleString() }} Fbu</td>
            <td>{{ payment.method }}</td>
            <td><span :class="['badge', getBadgeClass(payment.status)]">{{ translateStatus(payment.status) }}</span></td>
            <td>
              <div class="btn-group">
                <button class="btn-icon view" title="Voir" @click="viewPayment(payment)"><i class="fas fa-eye"></i></button>
                <button class="btn-icon delete" title="Supprimer" @click="confirmDelete(payment)"><i class="fas fa-trash-alt"></i></button>
              </div>
            </td>
          </tr>
          <tr v-if="filteredPayments.length === 0">
            <td colspan="8" class="empty-cell">Aucun paiement enregistré</td>
          </tr>
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
              {{ b.customer_name }} - {{ b.hall_name }} (reste: {{ toNumber(b.remaining_amount).toLocaleString() }} Fbu)
            </option>
          </select>
        </div>

        <div v-if="selectedBookingForForm" class="booking-summary">
          <div><strong>Total:</strong> {{ toNumber(selectedBookingForForm.total_price).toLocaleString() }} Fbu</div>
          <div><strong>Déjà payé:</strong> {{ toNumber(selectedBookingForForm.paid_amount).toLocaleString() }} Fbu</div>
          <div><strong>Reste:</strong> {{ toNumber(selectedBookingForForm.remaining_amount).toLocaleString() }} Fbu</div>
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
            <input v-model.number="form.amount" type="number" class="form-input" min="1" required />
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
        <button class="btn btn-primary" @click="savePayment">Enregistrer</button>
      </template>
    </AdminAppModal>

    <AdminAppModal v-model="showViewModal" title="Détails du paiement" width="420px">
      <div v-if="selectedPayment" class="view-details">
        <div class="detail-item"><span class="detail-label">Client</span><span class="detail-val">{{ selectedPayment.booking_customer_name }}</span></div>
        <div class="detail-item"><span class="detail-label">Réservation</span><span class="detail-val">{{ selectedPayment.booking_hall_name }}</span></div>
        <div class="detail-item"><span class="detail-label">Période</span><span class="detail-val">{{ selectedPayment.booking_start_date }} → {{ selectedPayment.booking_end_date }}</span></div>
        <div class="detail-item"><span class="detail-label">Type</span><span class="detail-val">{{ selectedPayment.kind === 'full' ? 'Paiement total' : 'Avance' }}</span></div>
        <div class="detail-item"><span class="detail-label">Montant</span><span class="detail-val">{{ toNumber(selectedPayment.amount).toLocaleString() }} Fbu</span></div>
        <div class="detail-item"><span class="detail-label">Reste après paiement</span><span class="detail-val">{{ toNumber(selectedPayment.booking_remaining_amount).toLocaleString() }} Fbu</span></div>
      </div>
      <template #footer>
        <button class="btn btn-primary" @click="showViewModal = false">Fermer</button>
      </template>
    </AdminAppModal>

    <AdminAppModal v-model="showDeleteModal" title="Confirmer la suppression" width="400px">
      <p>Supprimer le paiement <strong>{{ selectedPayment?.reference }}</strong> ?</p>
      <template #footer>
        <button class="btn btn-outline" @click="showDeleteModal = false">Annuler</button>
        <button class="btn btn-danger" @click="deletePayment">Supprimer</button>
      </template>
    </AdminAppModal>
  </div>
</template>

<script setup>
import { notify } from '~/composables/useNotification'
import { api } from '~/composables/useApi'

definePageMeta({ layout: 'admin' })
const route = useRoute()

const payments = ref([])
const bookings = ref([])
const exportRef = ref(null)
const search = ref('')
const statusFilter = ref('')
const methodFilter = ref('')
const dateFrom = ref('')
const dateTo = ref('')

const exportXls = () => {
  if (!exportRef.value) return
  const html = `<!doctype html><html><head><meta charset="utf-8"></head><body>${exportRef.value.innerHTML}</body></html>`
  const blob = new Blob([html], { type: 'application/vnd.ms-excel' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'payments.xls'
  a.click()
  URL.revokeObjectURL(url)
}

const exportPdf = () => {
  if (!exportRef.value) return
  const win = window.open('', '_blank')
  if (!win) return
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

const selectedBookingForForm = computed(() => unpaidBookings.value.find(b => b.id === form.value.booking) || null)
const totalRevenue = computed(() => payments.value.filter(p => p.status === 'paid').reduce((a, p) => a + toNumber(p.amount), 0))
const totalRemaining = computed(() => unpaidBookings.value.reduce((a, b) => a + toNumber(b.remaining_amount), 0))
const methods = computed(() => Array.from(new Set((payments.value || []).map(p => p.method).filter(Boolean))).sort())

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

const fetchPayments = async () => {
  try {
    const { data } = await api.get('payments/')
    payments.value = data
  } catch {
    notify('Erreur lors du chargement des paiements', 'danger')
  }
}

const fetchBookings = async () => {
  try {
    const { data } = await api.get('bookings/')
    bookings.value = data
  } catch {
    notify('Erreur lors du chargement des réservations', 'danger')
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
  try {
    await api.post('payments/', form.value)
    notify('Paiement enregistré avec succès', 'success')
    showFormModal.value = false
    await Promise.all([fetchPayments(), fetchBookings()])
  } catch {
    notify('Erreur lors de l\'enregistrement du paiement', 'danger')
  }
}

const viewPayment = (payment) => {
  selectedPayment.value = payment
  showViewModal.value = true
}

const confirmDelete = (payment) => {
  selectedPayment.value = payment
  showDeleteModal.value = true
}

const deletePayment = async () => {
  try {
    await api.delete(`payments/${selectedPayment.value.id}/`)
    notify('Paiement supprimé', 'danger')
    showDeleteModal.value = false
    await Promise.all([fetchPayments(), fetchBookings()])
  } catch {
    notify('Erreur lors de la suppression', 'danger')
  }
}

const translateStatus = (status) => ({ paid: 'Complété', pending: 'En attente', failed: 'Échoué' }[status] || status)
const getBadgeClass = (status) => ({ paid: 'badge-success', pending: 'badge-warning', failed: 'badge-danger' }[status] || '')

onMounted(async () => {
  await Promise.all([fetchPayments(), fetchBookings()])
  if (route.query.booking) openAddModal()
})
</script>

<style scoped>
.payments-page { padding: 0; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--space-8); }
.page-header h1 { font-size: 1.75rem; font-weight: 800; margin: 0; color: #0f172a; }
.page-header p { color: #64748b; margin-top: .35rem; }
.header-actions { display: inline-flex; gap: .5rem; flex-wrap: wrap; align-items: center; justify-content: flex-end; }

.controls { display: flex; gap: var(--space-4); margin-bottom: var(--space-8); padding: var(--space-4) var(--space-6); align-items: center; flex-wrap: wrap; }
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
</style>
