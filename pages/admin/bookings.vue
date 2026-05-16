<!-- pages/admin/bookings.vue -->
<template>
  <div class="bookings-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1>Réservations</h1>
        <p>Gérer toutes les réservations de salle</p>
      </div>
      <div class="header-actions">
        <button class="btn btn-export btn-sm" @click="exportPdf">
          <i class="fas fa-file-pdf"></i> Export PDF
        </button>
        <button class="btn btn-export btn-sm" @click="exportXls">
          <i class="fas fa-file-excel"></i> Export XLS
        </button>
        <NuxtLink to="/admin/calendar" class="btn btn-secondary btn-sm">
          <i class="fas fa-calendar-alt"></i> Calendrier global
        </NuxtLink>
        <button class="btn btn-primary btn-sm" @click="openAddModal">
          <i class="fas fa-plus"></i> Nouvelle réservation
        </button>
      </div>
    </div>

    <!-- Controls -->
    <div class="controls card">
      <div class="search-wrapper">
        <i class="fas fa-search search-icon"></i>
        <input
          type="text"
          v-model="search"
          placeholder="Rechercher par client ou salle..."
          class="search-input-clean"
        />
      </div>
      <div class="filter-wrapper">
        <select v-model="statusFilter" class="filter-select-clean">
          <option value="">Tous les statuts</option>
          <option value="pending">En attente</option>
          <option value="confirmed">Confirmé</option>
          <option value="paid">Payé</option>
          <option value="cancelled">Annulé</option>
        </select>
      </div>
      <div class="filter-wrapper">
        <select v-model="hallFilter" class="filter-select-clean">
          <option value="">Toutes les salles</option>
          <option v-for="h in halls" :key="h.id" :value="h.id">{{ h.name }}</option>
        </select>
      </div>
      <div class="filter-wrapper">
        <select v-model="eventTypeFilter" class="filter-select-clean">
          <option value="">Tous les événements</option>
          <option value="Mariage">Mariage</option>
          <option value="Séminaire">Séminaire</option>
          <option value="Gala">Gala</option>
          <option value="Anniversaire">Anniversaire</option>
          <option value="Réunion">Réunion</option>
        </select>
      </div>
      <div class="filter-wrapper">
        <input v-model="dateFrom" type="date" class="filter-input-clean" />
      </div>
      <div class="filter-wrapper">
        <input v-model="dateTo" type="date" class="filter-input-clean" />
      </div>
      <div class="filter-wrapper">
        <input v-model.number="minAmount" type="number" class="filter-input-clean" placeholder="Min (Fbu)" />
      </div>
      <div class="filter-wrapper">
        <input v-model.number="maxAmount" type="number" class="filter-input-clean" placeholder="Max (Fbu)" />
      </div>
    </div>

    <!-- Table -->
    <div class="table-container card">
      <h2 class="table-title">
        Toutes les réservations ({{ filteredBookings.length }})
      </h2>
      <div class="table-wrapper">
        <table ref="tableRef" class="bookings-table admin-table">
          <thead>
            <tr>
              <th>Client</th>
              <th>Salle</th>
              <th>Événement</th>
              <th>Dates</th>
              <th>Montant</th>
              <th>Statut</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="booking in filteredBookings" :key="booking.id">
              <td class="customer-cell">
                <div class="customer-name">{{ booking.customer_name }}</div>
                <div class="customer-email">{{ booking.customer_email }}</div>
              </td>
              <td>{{ booking.hall_name }}</td>
              <td>{{ booking.event_type }}</td>
              <td class="date-cell">
                <div>{{ booking.start_date }}</div>
                <div class="end-date">au {{ booking.end_date }}</div>
              </td>
              <td class="amount-cell">{{ booking.total_price.toLocaleString() }} Fbu</td>
              <td>
                <span :class="['badge', getBadgeClass(booking.status)]">
                  {{ getStatusTranslation(booking.status) }}
                </span>
              </td>
              <td class="actions-cell">
                <div class="btn-group">
                  <NuxtLink class="btn-icon pay" :to="`/admin/payments?booking=${booking.id}`" title="Payer">
                    <i class="fas fa-coins"></i>
                  </NuxtLink>
                  <button class="btn-icon approve" v-if="booking.status === 'pending'" @click="approve(booking)" title="Approuver">
                    <i class="fas fa-check-circle"></i>
                  </button>
                  <button class="btn-icon reject" v-if="booking.status === 'pending'" @click="reject(booking)" title="Rejeter">
                    <i class="fas fa-times-circle"></i>
                  </button>
                  <button class="btn-icon view" @click="viewBooking(booking)" title="Voir les détails">
                    <i class="fas fa-eye"></i>
                  </button>
                  <button class="btn-icon edit" @click="editBooking(booking)" title="Modifier">
                    <i class="fas fa-edit"></i>
                  </button>
                  <button class="btn-icon delete" @click="confirmDelete(booking)" title="Supprimer">
                    <i class="fas fa-trash-alt"></i>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Modals -->
    <AdminAppModal v-model="showFormModal" :title="isEditing ? 'Modifier la réservation' : 'Nouvelle réservation'" width="600px">
      <form @submit.prevent="saveBooking" class="admin-form">
        <div class="form-grid">
          <div class="form-group full">
            <label class="form-label">Client</label>
            <input v-model="form.customer_name" type="text" class="form-input" placeholder="Nom complet" required />
          </div>
          <div class="form-group full">
            <label class="form-label">Email</label>
            <input v-model="form.customer_email" type="email" class="form-input" placeholder="email@exemple.com" required />
          </div>
          <div class="form-group">
            <label class="form-label">Salle</label>
            <select v-model="form.hall" class="form-select" required @change="calculatePrice">
              <option v-for="h in halls" :key="h.id" :value="h.id">{{ h.name }}</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Type d'événement</label>
            <select v-model="form.event_type" class="form-select" required>
              <option value="Mariage">Mariage</option>
              <option value="Séminaire">Séminaire</option>
              <option value="Gala">Gala</option>
              <option value="Anniversaire">Anniversaire</option>
              <option value="Réunion">Réunion</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Date Début</label>
            <input v-model="form.start_date" type="date" class="form-input" required @change="calculatePrice" />
          </div>
          <div class="form-group">
            <label class="form-label">Date Fin</label>
            <input v-model="form.end_date" type="date" class="form-input" required @change="calculatePrice" />
          </div>
          <div class="form-group">
            <label class="form-label">Montant (Fbu)</label>
            <input v-model.number="form.total_price" type="number" class="form-input" required />
            <small class="form-hint" v-if="daysCount > 0">{{ daysCount }} jour(s) à {{ pricePerDay.toLocaleString() }} Fbu/jour</small>
          </div>
        </div>
      </form>
      <template #footer>
        <button class="btn btn-outline" @click="showFormModal = false">Annuler</button>
        <button class="btn btn-primary" @click="saveBooking">{{ isEditing ? 'Mettre à jour' : 'Créer' }}</button>
      </template>
    </AdminAppModal>

    <!-- View Modal -->
    <AdminAppModal v-model="showViewModal" title="Détails de la réservation" width="500px">
      <div v-if="selectedBooking" class="view-details">
        <div class="detail-item">
          <span class="detail-label">Client</span>
          <span class="detail-val">{{ selectedBooking.customer_name }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">Email</span>
          <span class="detail-val">{{ selectedBooking.customer_email }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">Salle</span>
          <span class="detail-val">{{ selectedBooking.hall_name }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">Événement</span>
          <span class="detail-val">{{ selectedBooking.event_type }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">Période</span>
          <span class="detail-val">{{ selectedBooking.start_date }} au {{ selectedBooking.end_date }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">Montant</span>
          <span class="detail-val">{{ selectedBooking.total_price.toLocaleString() }} Fbu</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">Statut</span>
          <span :class="['badge', getBadgeClass(selectedBooking.status)]">
            {{ getStatusTranslation(selectedBooking.status) }}
          </span>
        </div>
      </div>
      <template #footer>
        <button class="btn btn-primary" @click="showViewModal = false">Fermer</button>
      </template>
    </AdminAppModal>

    <!-- Delete Confirmation Modal -->
    <AdminAppModal v-model="showDeleteModal" title="Confirmer la suppression" width="400px">
      <p>Êtes-vous sûr de vouloir supprimer la réservation de <strong>{{ selectedBooking?.customer_name }}</strong> ? Cette action est irréversible.</p>
      <template #footer>
        <button class="btn btn-outline" @click="showDeleteModal = false">Annuler</button>
        <button class="btn btn-danger" @click="deleteBooking">Supprimer</button>
      </template>
    </AdminAppModal>

    <div class="static-info">
      <p><i class="fas fa-info-circle"></i> Affichage de données statiques (Mode Démo)</p>
    </div>
  </div>
</template>

<script setup>
import { notify } from '~/composables/useNotification'
import { api } from '~/composables/useApi'

definePageMeta({ layout: 'admin' })

const search = ref('')
const statusFilter = ref('')
const hallFilter = ref('')
const eventTypeFilter = ref('')
const dateFrom = ref('')
const dateTo = ref('')
const minAmount = ref(null)
const maxAmount = ref(null)
const showFormModal = ref(false)
const showViewModal = ref(false)
const showDeleteModal = ref(false)
const isEditing = ref(false)
const selectedBooking = ref(null)
const tableRef = ref(null)

const exportXls = () => {
  if (!tableRef.value) return
  const html = `<!doctype html><html><head><meta charset="utf-8"></head><body>${tableRef.value.outerHTML}</body></html>`
  const blob = new Blob([html], { type: 'application/vnd.ms-excel' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'bookings.xls'
  a.click()
  URL.revokeObjectURL(url)
}

const exportPdf = () => {
  if (!tableRef.value) return
  const win = window.open('', '_blank')
  if (!win) return
  win.document.write(`<!doctype html><html><head><meta charset="utf-8"><title>Réservations</title><style>
  body{font-family:Arial, sans-serif; padding:20px}
  table{width:100%; border-collapse:collapse}
  th,td{border:1px solid #e2e8f0; padding:8px; text-align:left; font-size:12px}
  th{background:#f8fafc}
  </style></head><body><h2>Réservations</h2>${tableRef.value.outerHTML}</body></html>`)
  win.document.close()
  win.focus()
  win.print()
  win.close()
}

const form = ref({
  id: null,
  customer_name: '',
  customer_email: '',
  hall: '',
  event_type: 'Mariage',
  start_date: '',
  end_date: '',
  total_price: 0,
  status: 'pending'
})

const bookings = ref([])
const halls = ref([])

const fetchBookings = async () => {
  try {
    const response = await api.get('bookings/')
    bookings.value = response.data
  } catch (error) {
    notify('Erreur lors du chargement des réservations', 'danger')
  }
}

const fetchHalls = async () => {
  try {
    const response = await api.get('halls/')
    halls.value = response.data
    if (halls.value.length > 0 && !form.value.hall) {
      form.value.hall = halls.value[0].id
    }
  } catch (error) {
    notify('Erreur lors du chargement des salles', 'danger')
  }
}

onMounted(() => {
  fetchBookings()
  fetchHalls()
})

const pricePerDay = ref(0)
const daysCount = ref(0)

const calculatePrice = () => {
  if (form.value.start_date && form.value.end_date && form.value.hall) {
    const start = new Date(form.value.start_date)
    const end = new Date(form.value.end_date)
    const diffTime = Math.abs(end - start)
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1
    daysCount.value = diffDays
    
    const hall = halls.value.find(h => h.id === form.value.hall)
    if (hall) {
      pricePerDay.value = hall.price_per_day
      form.value.total_price = diffDays * hall.price_per_day
    }
  }
}

const filteredBookings = computed(() => {
  return bookings.value.filter(b => {
    const q = search.value.toLowerCase().trim()
    const matchesSearch = q === '' ||
      b.customer_name.toLowerCase().includes(q) ||
      b.customer_email.toLowerCase().includes(q) ||
      b.hall_name.toLowerCase().includes(q)
    const matchesStatus = statusFilter.value === '' || b.status === statusFilter.value
    const matchesHall = hallFilter.value === '' || String(b.hall) === String(hallFilter.value) || String(b.hall_id) === String(hallFilter.value)
    const matchesEventType = eventTypeFilter.value === '' || b.event_type === eventTypeFilter.value

    const start = b.start_date ? new Date(b.start_date) : null
    const fromOk = !dateFrom.value || (start && start >= new Date(dateFrom.value))
    const toOk = !dateTo.value || (start && start <= new Date(dateTo.value))

    const amount = Number(b.total_price || 0)
    const minOk = minAmount.value == null || minAmount.value === '' || amount >= Number(minAmount.value)
    const maxOk = maxAmount.value == null || maxAmount.value === '' || amount <= Number(maxAmount.value)

    return matchesSearch && matchesStatus && matchesHall && matchesEventType && fromOk && toOk && minOk && maxOk
  })
})

const saveBooking = async () => {
  try {
    if (isEditing.value) {
      await api.put(`bookings/${form.value.id}/`, form.value)
      notify('Réservation mise à jour avec succès', 'success')
    } else {
      await api.post('bookings/', form.value)
      notify('Nouvelle réservation créée', 'success')
    }
    showFormModal.value = false
    fetchBookings()
  } catch (error) {
    notify('Erreur lors de l\'enregistrement', 'danger')
  }
}

const deleteBooking = async () => {
  try {
    await api.delete(`bookings/${selectedBooking.value.id}/`)
    notify('Réservation supprimée', 'danger')
    showDeleteModal.value = false
    fetchBookings()
  } catch (error) {
    notify('Erreur lors de la suppression', 'danger')
  }
}

const approve = async (booking) => {
  try {
    await api.patch(`bookings/${booking.id}/`, { status: 'confirmed' })
    notify(`Réservation de ${booking.customer_name} approuvée`, 'success')
    fetchBookings()
  } catch (error) {
    notify('Erreur lors de l\'approbation', 'danger')
  }
}

const reject = async (booking) => {
  try {
    await api.patch(`bookings/${booking.id}/`, { status: 'cancelled' })
    notify(`Réservation de ${booking.customer_name} rejetée`, 'warning')
    fetchBookings()
  } catch (error) {
    notify('Erreur lors du rejet', 'danger')
  }
}

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

const openAddModal = () => {
  isEditing.value = false
  form.value = { id: null, customer_name: '', customer_email: '', hall: halls.value[0]?.id || '', event_type: 'Mariage', start_date: '', end_date: '', total_price: 0, status: 'pending' }
  daysCount.value = 0
  showFormModal.value = true
}

const editBooking = (booking) => {
  isEditing.value = true
  form.value = { ...booking }
  calculatePrice()
  showFormModal.value = true
}

const viewBooking = (booking) => {
  selectedBooking.value = booking
  showViewModal.value = true
}

const confirmDelete = (booking) => {
  selectedBooking.value = booking
  showDeleteModal.value = true
}
</script>

<style scoped>
.bookings-page {
  padding: 0;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-10);
}

.page-header h1 {
  font-size: 1.75rem;
  font-weight: 800;
  color: #0f172a;
  margin-bottom: 0;
}

.page-header p {
  color: #64748b;
  font-size: 0.9rem;
  font-weight: 500;
}

.header-actions {
  display: flex;
  gap: var(--space-3);
}

.controls {
  display: flex;
  gap: var(--space-4);
  margin-bottom: var(--space-8);
  padding: var(--space-4) var(--space-6);
  align-items: center;
  height: auto;
  flex-wrap: wrap;
}

.search-wrapper {
  flex-grow: 1;
  position: relative;
}

.search-icon {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: #94a3b8;
  font-size: 0.9rem;
}

.search-input-clean {
  width: 100%;
  padding: 0.625rem 1rem 0.625rem 2.5rem;
  border: 1px solid #e2e8f0;
  border-radius: var(--rounded-md);
  font-size: 0.9rem;
  background: #f8fafc;
  transition: var(--transition-fast);
}

.search-input-clean:focus {
  background: white;
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(212, 175, 55, 0.1);
}

.filter-select-clean {
  padding: 0.625rem 2rem 0.625rem 1rem;
  border: 1px solid #e2e8f0;
  border-radius: var(--rounded-md);
  font-size: 0.9rem;
  background: #f8fafc;
  color: #475569;
  font-weight: 600;
  cursor: pointer;
}

.filter-input-clean {
  padding: 0.625rem 1rem;
  border: 1px solid #e2e8f0;
  border-radius: var(--rounded-md);
  font-size: 0.9rem;
  background: #f8fafc;
  color: #475569;
  font-weight: 600;
  transition: var(--transition-fast);
}

.filter-input-clean:focus {
  background: white;
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(212, 175, 55, 0.1);
}

.table-title {
  font-size: 1rem;
  font-weight: 800;
  margin-bottom: var(--space-6);
  color: #1e293b;
  padding: 0 var(--space-2);
}

.bookings-table {
  width: 100%;
}

.customer-name {
  font-weight: 700;
  color: #0f172a;
  font-size: 0.95rem;
}

.customer-email {
  font-size: 0.8rem;
  color: #94a3b8;
  font-weight: 500;
}

.amount-cell {
  font-weight: 800;
  color: #0f172a;
  font-size: 0.9rem;
}

.btn-icon {
  width: 34px;
  height: 34px;
  font-size: 1.1rem;
  background: #f8fafc;
  color: #94a3b8;
}

.btn-icon:hover {
  background: #f1f5f9;
}

.btn-icon.approve:hover { color: var(--success); }
.btn-icon.reject:hover { color: var(--warning); }
.btn-icon.view:hover { color: var(--info); }
.btn-icon.edit:hover { color: var(--primary); }
.btn-icon.delete:hover { color: var(--danger); }
.btn-icon.pay:hover { color: #b45309; }

.view-details {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.detail-item {
  display: flex;
  justify-content: space-between;
  padding-bottom: var(--space-3);
  border-bottom: 1px solid #f1f5f9;
}

.detail-label {
  font-weight: 700;
  color: #64748b;
  font-size: 0.85rem;
  text-transform: uppercase;
}

.detail-val {
  font-weight: 600;
  color: #0f172a;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-4);
}

.form-group.full {
  grid-column: span 2;
}

.static-info {
  margin-top: var(--space-12);
  color: #cbd5e1;
  font-size: 0.85rem;
  text-align: center;
  font-weight: 600;
}
</style>
