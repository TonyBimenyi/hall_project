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
        <button class="btn btn-export btn-sm" :class="{ 'is-loading': exportingPdf }" :disabled="exportingPdf || exportingXls" @click="exportPdf">
          <i class="fas fa-file-pdf"></i> Export PDF
        </button>
        <button class="btn btn-export btn-sm" :class="{ 'is-loading': exportingXls }" :disabled="exportingPdf || exportingXls" @click="exportXls">
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
      <div class="controls-top">
        <div class="search-wrapper">
          <i class="fas fa-search search-icon"></i>
          <input
            type="text"
            v-model="search"
            placeholder="Rechercher par client ou salle..."
            class="search-input-clean"
          />
        </div>
        <button class="btn-icon filters-toggle" :class="{ active: filtersOpen }" title="Filtres" @click="filtersOpen = !filtersOpen">
          <i class="fas fa-filter"></i>
        </button>
      </div>
      <div v-show="!isMobile || filtersOpen" class="filters-panel">
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
            <option value="Autres">Autres</option>
          </select>
        </div>
        <div class="filter-wrapper">
          <input v-model="dateFrom" type="date" class="filter-input-clean" />
        </div>
        <div class="filter-wrapper">
          <input v-model="dateTo" type="date" class="filter-input-clean" />
        </div>
        <div class="filter-wrapper">
          <input v-model="minAmountInput" inputmode="numeric" type="text" class="filter-input-clean" placeholder="Min (Fbu)" />
        </div>
        <div class="filter-wrapper">
          <input v-model="maxAmountInput" inputmode="numeric" type="text" class="filter-input-clean" placeholder="Max (Fbu)" />
        </div>
      </div>
    </div>

    <!-- Table -->
    <div class="table-container card">
      <div style="display:flex; align-items:center; justify-content:space-between; gap:12px; flex-wrap:wrap; margin-bottom: var(--space-4);">
        <h2 class="table-title" style="margin-bottom:0;">
          Toutes les réservations ({{ loadingBookings ? '...' : filteredBookings.length }})
        </h2>
        <AdminAppTablePagination
          :start="bookingsStartIndex"
          :end="bookingsEndIndex"
          :total="bookingsTotalItems"
          :can-prev="bookingsCanPrev"
          :can-next="bookingsCanNext"
          :disabled="loadingBookings"
          @prev="bookingsPrevPage"
          @next="bookingsNextPage"
        />
      </div>
      <div v-if="isMobile" class="admin-cards">
        <template v-if="loadingBookings">
          <div v-for="n in 6" :key="`sk-card-${n}`" class="admin-card">
            <div class="admin-card-head">
              <div style="width: 100%;">
                <div class="skeleton-line skeleton-w-70"></div>
                <div style="margin-top: 8px;" class="skeleton-line skeleton-w-50"></div>
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
          <div v-for="booking in paginatedBookings" :key="booking.id" class="admin-card has-actions">
            <div class="admin-card-head">
              <div>
                <div class="admin-card-title">{{ booking.customer_name }}</div>
                <div class="admin-card-subtitle">{{ getBookingDisplayId(booking) }} • {{ booking.hall_name }} • {{ formatDateRange(booking.start_date, booking.end_date) }}</div>
              </div>

              <div class="admin-card-actions">
                <div class="actions-dropdown">
                <button class="btn-icon details" title="Détails" @click.stop="toggleActions(booking.id)">
                  <i class="fas fa-ellipsis-vertical"></i>
                </button>
                <div v-if="openActionsId === booking.id" class="actions-menu" @click.stop>
                  <NuxtLink class="actions-item" :to="`/admin/payments?booking=${booking.id}`" @click="closeActions">
                    <i class="fas fa-coins"></i> Payer
                  </NuxtLink>
                  <button
                    v-if="booking.status === 'pending'"
                    class="actions-item"
                    :class="{ 'is-loading': actionBookingId === booking.id && actionType === 'approve' }"
                    :disabled="actionBookingId === booking.id"
                    @click="approve(booking)"
                  >
                    <i class="fas fa-check-circle"></i> Approuver
                  </button>
                  <button
                    v-if="booking.status === 'pending'"
                    class="actions-item"
                    :class="{ 'is-loading': actionBookingId === booking.id && actionType === 'reject' }"
                    :disabled="actionBookingId === booking.id"
                    @click="reject(booking)"
                  >
                    <i class="fas fa-times-circle"></i> Rejeter
                  </button>
                  <button class="actions-item" @click="viewBooking(booking)">
                    <i class="fas fa-eye"></i> Voir
                  </button>
                  <button class="actions-item" @click="editBooking(booking)">
                    <i class="fas fa-edit"></i> Modifier
                  </button>
                  <button class="actions-item danger" @click="confirmDelete(booking)">
                    <i class="fas fa-trash-alt"></i> Supprimer
                  </button>
                </div>
                </div>
              </div>
            </div>

            <div class="admin-card-body">
              <div class="admin-kv">
                <span class="k">ID</span>
                <span class="v">{{ getBookingDisplayId(booking) }}</span>
              </div>
              <div class="admin-kv">
                <span class="k">Événement</span>
                <span class="v">{{ booking.event_type }}</span>
              </div>
              <div class="admin-kv">
                <span class="k">Montant</span>
                <span class="v">{{ formatMoney(booking.total_price) }}</span>
              </div>
              <div class="admin-kv">
                <span class="k">Statut</span>
                <span class="v">
                  <span :class="['badge', getBadgeClass(booking.status)]">{{ getStatusTranslation(booking.status) }}</span>
                </span>
              </div>
            </div>
          </div>
        </template>
        <div v-if="!loadingBookings && filteredBookings.length === 0" class="empty-cell">Aucune réservation</div>
      </div>

      <div v-else class="table-wrapper">
        <table ref="tableRef" class="bookings-table admin-table">
          <thead>
            <tr>
              <th><button class="table-sort-btn" :class="{ active: isBookingSortActive('id') }" @click="toggleBookingSort('id')">ID <i :class="bookingSortIconClass('id')"></i></button></th>
              <th><button class="table-sort-btn" :class="{ active: isBookingSortActive('customer_name') }" @click="toggleBookingSort('customer_name')">Client <i :class="bookingSortIconClass('customer_name')"></i></button></th>
              <th><button class="table-sort-btn" :class="{ active: isBookingSortActive('hall_name') }" @click="toggleBookingSort('hall_name')">Salle <i :class="bookingSortIconClass('hall_name')"></i></button></th>
              <th><button class="table-sort-btn" :class="{ active: isBookingSortActive('event_type') }" @click="toggleBookingSort('event_type')">Événement <i :class="bookingSortIconClass('event_type')"></i></button></th>
              <th><button class="table-sort-btn" :class="{ active: isBookingSortActive('start_date') }" @click="toggleBookingSort('start_date')">Dates <i :class="bookingSortIconClass('start_date')"></i></button></th>
              <th><button class="table-sort-btn" :class="{ active: isBookingSortActive('total_price') }" @click="toggleBookingSort('total_price')">Montant <i :class="bookingSortIconClass('total_price')"></i></button></th>
              <th><button class="table-sort-btn" :class="{ active: isBookingSortActive('status') }" @click="toggleBookingSort('status')">Statut <i :class="bookingSortIconClass('status')"></i></button></th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <template v-if="loadingBookings">
              <tr v-for="n in 6" :key="`sk-${n}`">
                <td><div class="skeleton-line skeleton-w-50"></div></td>
                <td class="customer-cell">
                  <div class="skeleton-lines">
                    <div class="skeleton-line skeleton-w-70"></div>
                    <div class="skeleton-line skeleton-w-50"></div>
                  </div>
                </td>
                <td><div class="skeleton-line skeleton-w-60"></div></td>
                <td><div class="skeleton-line skeleton-w-50"></div></td>
                <td class="date-cell">
                  <div class="skeleton-lines">
                    <div class="skeleton-line skeleton-w-60"></div>
                    <div class="skeleton-line skeleton-w-40"></div>
                  </div>
                </td>
                <td class="amount-cell"><div class="skeleton-line skeleton-w-50"></div></td>
                <td><div class="skeleton-line skeleton-w-40"></div></td>
                <td class="actions-cell"><div class="skeleton-line skeleton-w-60"></div></td>
              </tr>
            </template>
            <tr v-else v-for="booking in paginatedBookings" :key="booking.id">
              <td><code>{{ getBookingDisplayId(booking) }}</code></td>
              <td class="customer-cell">
                <div class="customer-name">{{ booking.customer_name }}</div>
                <div class="customer-email">{{ booking.customer_email }}</div>
              </td>
              <td>{{ booking.hall_name }}</td>
              <td>{{ booking.event_type }}</td>
              <td class="date-cell">{{ formatDateRange(booking.start_date, booking.end_date) }}</td>
              <td class="amount-cell">{{ formatMoney(booking.total_price) }}</td>
              <td>
                <span :class="['badge', getBadgeClass(booking.status)]">
                  {{ getStatusTranslation(booking.status) }}
                </span>
              </td>
              <td class="actions-cell">
                <div class="actions-dropdown">
                  <button class="btn-icon details" title="Détails" @click.stop="toggleActions(booking.id)">
                    <i class="fas fa-ellipsis-vertical"></i>
                  </button>
                  <div v-if="openActionsId === booking.id" class="actions-menu" @click.stop>
                    <NuxtLink class="actions-item" :to="`/admin/payments?booking=${booking.id}`" @click="closeActions">
                      <i class="fas fa-coins"></i> Payer
                    </NuxtLink>
                    <button v-if="booking.status === 'pending'" class="actions-item" :class="{ 'is-loading': actionBookingId === booking.id && actionType === 'approve' }" :disabled="actionBookingId === booking.id" @click="approve(booking)">
                      <i class="fas fa-check-circle"></i> Approuver
                    </button>
                    <button v-if="booking.status === 'pending'" class="actions-item" :class="{ 'is-loading': actionBookingId === booking.id && actionType === 'reject' }" :disabled="actionBookingId === booking.id" @click="reject(booking)">
                      <i class="fas fa-times-circle"></i> Rejeter
                    </button>
                    <button class="actions-item" @click="viewBooking(booking)">
                      <i class="fas fa-eye"></i> Voir
                    </button>
                    <button class="actions-item" @click="editBooking(booking)">
                      <i class="fas fa-edit"></i> Modifier
                    </button>
                    <button class="actions-item danger" @click="confirmDelete(booking)">
                      <i class="fas fa-trash-alt"></i> Supprimer
                    </button>
                  </div>
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
            <input v-model="form.customer_email" type="email" class="form-input" placeholder="email@exemple.com" />
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
              <option v-for="eventOption in eventTypeOptions" :key="eventOption" :value="eventOption">{{ eventOption }}</option>
            </select>
          </div>
          <div v-if="isOtherEventType" class="form-group full">
            <label class="form-label">Détails de l'événement</label>
            <textarea
              v-model="form.event_type_other"
              class="form-textarea"
              rows="3"
              required
              placeholder="Précisez le type d'événement"
            ></textarea>
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
            <input v-model="totalPriceInput" inputmode="numeric" type="text" class="form-input" required />
            <small class="form-hint" v-if="daysCount > 0">{{ daysCount }} jour(s) à {{ formatMoney(pricePerDay) }}/jour</small>
          </div>
        </div>
      </form>
      <template #footer>
        <button class="btn btn-outline" @click="showFormModal = false">Annuler</button>
        <button class="btn btn-primary" :class="{ 'is-loading': savingBooking }" :disabled="savingBooking" @click="saveBooking">{{ isEditing ? 'Mettre à jour' : 'Créer' }}</button>
      </template>
    </AdminAppModal>

    <!-- View Modal -->
    <AdminAppModal v-model="showViewModal" title="Détails de la réservation" width="500px">
      <div v-if="selectedBooking" class="view-details">
        <div class="detail-item">
          <span class="detail-label">ID</span>
          <span class="detail-val">{{ getBookingDisplayId(selectedBooking) }}</span>
        </div>
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
          <span class="detail-val">{{ formatDateRange(selectedBooking.start_date, selectedBooking.end_date) }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">Montant</span>
          <span class="detail-val">{{ formatMoney(selectedBooking.total_price) }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">Statut</span>
          <span :class="['badge', getBadgeClass(selectedBooking.status)]">
            {{ getStatusTranslation(selectedBooking.status) }}
          </span>
        </div>
        <div class="detail-item">
          <span class="detail-label">Créé par</span>
          <span class="detail-val">{{ selectedBooking.created_by_name || '-' }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">Dernière action par</span>
          <span class="detail-val">{{ selectedBooking.updated_by_name || selectedBooking.created_by_name || '-' }}</span>
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
        <button class="btn btn-danger" :class="{ 'is-loading': deletingBooking }" :disabled="deletingBooking" @click="deleteBooking">Supprimer</button>
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
import { useTableSort } from '~/composables/useTableSort'

definePageMeta({ layout: 'admin' })
const { formatMoney, formatNumberSpaces, moneyInputModel, parseMoney } = useMoney()
const { formatDateRange, formatDisplayDate } = useDateFormat()
const { buildMonthlySequenceMap } = useDisplayIds()
const eventTypeOptions = ['Mariage', 'Séminaire', 'Gala', 'Anniversaire', 'Réunion', 'Autres']

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
const exportingPdf = ref(false)
const exportingXls = ref(false)
const savingBooking = ref(false)
const deletingBooking = ref(false)
const actionBookingId = ref(null)
const actionType = ref('')
const loadingBookings = ref(false)
const loadingHalls = ref(false)
const isMobile = ref(false)
const filtersOpen = ref(false)
const openActionsId = ref(null)

const exportXls = async () => {
  if (!tableRef.value) return
  exportingXls.value = true
  await nextTick()
  const html = `<!doctype html><html><head><meta charset="utf-8"></head><body>${tableRef.value.outerHTML}</body></html>`
  const blob = new Blob([html], { type: 'application/vnd.ms-excel' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'bookings.xls'
  a.click()
  URL.revokeObjectURL(url)
  setTimeout(() => {
    exportingXls.value = false
  }, 350)
}

const exportPdf = async () => {
  if (!tableRef.value) return
  exportingPdf.value = true
  await nextTick()
  const win = window.open('', '_blank')
  if (!win) {
    exportingPdf.value = false
    return
  }
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
  setTimeout(() => {
    exportingPdf.value = false
  }, 350)
}

const form = ref({
  id: null,
  customer_name: '',
  customer_email: '',
  hall: '',
  event_type: 'Mariage',
  event_type_other: '',
  start_date: '',
  end_date: '',
  total_price: 0,
  status: 'pending'
})
const isOtherEventType = computed(() => form.value.event_type === 'Autres')
const totalPriceInput = moneyInputModel(form, 'total_price')
const minAmountInput = computed({
  get: () => (minAmount.value === null || minAmount.value === '' ? '' : formatNumberSpaces(minAmount.value)),
  set: (value) => {
    minAmount.value = value === '' ? null : parseMoney(value)
  }
})
const maxAmountInput = computed({
  get: () => (maxAmount.value === null || maxAmount.value === '' ? '' : formatNumberSpaces(maxAmount.value)),
  set: (value) => {
    maxAmount.value = value === '' ? null : parseMoney(value)
  }
})

const bookings = ref([])
const halls = ref([])

const fetchBookings = async () => {
  loadingBookings.value = true
  try {
    const response = await api.get('bookings/')
    bookings.value = response.data
  } catch (error) {
    notify('Erreur lors du chargement des réservations', 'danger')
  } finally {
    loadingBookings.value = false
  }
}

const fetchHalls = async () => {
  loadingHalls.value = true
  try {
    const response = await api.get('halls/')
    halls.value = response.data
    if (halls.value.length > 0 && !form.value.hall) {
      form.value.hall = halls.value[0].id
    }
  } catch (error) {
    notify('Erreur lors du chargement des salles', 'danger')
  } finally {
    loadingHalls.value = false
  }
}

onMounted(() => {
  fetchBookings()
  fetchHalls()
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

const toggleActions = (id) => {
  openActionsId.value = openActionsId.value === id ? null : id
}

const closeActions = () => {
  openActionsId.value = null
}

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
      String(b.customer_name || '').toLowerCase().includes(q) ||
      String(b.customer_email || '').toLowerCase().includes(q) ||
      String(b.hall_name || '').toLowerCase().includes(q)
    const matchesStatus = statusFilter.value === '' || b.status === statusFilter.value
    const matchesHall = hallFilter.value === '' || String(b.hall) === String(hallFilter.value) || String(b.hall_id) === String(hallFilter.value)
    const matchesEventType = eventTypeFilter.value === '' || (eventTypeFilter.value === 'Autres'
      ? String(b.event_type || '').startsWith('Autres: ')
      : b.event_type === eventTypeFilter.value)

    const start = b.start_date ? new Date(b.start_date) : null
    const fromOk = !dateFrom.value || (start && start >= new Date(dateFrom.value))
    const toOk = !dateTo.value || (start && start <= new Date(dateTo.value))

    const amount = Number(b.total_price || 0)
    const minOk = minAmount.value == null || minAmount.value === '' || amount >= Number(minAmount.value)
    const maxOk = maxAmount.value == null || maxAmount.value === '' || amount <= Number(maxAmount.value)

    return matchesSearch && matchesStatus && matchesHall && matchesEventType && fromOk && toOk && minOk && maxOk
  })
})

const {
  sortedItems: sortedBookings,
  toggleSort: toggleBookingSort,
  isSortActive: isBookingSortActive,
  sortIconClass: bookingSortIconClass,
} = useTableSort(filteredBookings, {
  initialKey: 'id',
  initialDirection: 'desc',
  accessors: {
    total_price: booking => Number(booking?.total_price || 0),
  },
})

const bookingDisplayIds = computed(() => buildMonthlySequenceMap(bookings.value, 'LBR', booking => booking.start_date))
const getBookingDisplayId = (booking) => bookingDisplayIds.value.get(booking?.id) || 'LBR00000001'

const {
  paginatedItems: paginatedBookings,
  totalItems: bookingsTotalItems,
  startIndex: bookingsStartIndex,
  endIndex: bookingsEndIndex,
  canPrev: bookingsCanPrev,
  canNext: bookingsCanNext,
  prevPage: bookingsPrevPage,
  nextPage: bookingsNextPage,
} = usePagination(sortedBookings, 50)

const saveBooking = async () => {
  savingBooking.value = true
  try {
    const payload = buildBookingPayload()
    if (isEditing.value) {
      await api.put(`bookings/${form.value.id}/`, payload)
      notify('Réservation mise à jour avec succès', 'success')
    } else {
      await api.post('bookings/', payload)
      notify('Nouvelle réservation créée', 'success')
    }
    showFormModal.value = false
    fetchBookings()
  } catch (error) {
    notify('Erreur lors de l\'enregistrement', 'danger')
  } finally {
    savingBooking.value = false
  }
}

const deleteBooking = async () => {
  if (!selectedBooking.value?.id) return
  deletingBooking.value = true
  try {
    await api.delete(`bookings/${selectedBooking.value.id}/`)
    notify('Réservation supprimée', 'danger')
    showDeleteModal.value = false
    fetchBookings()
  } catch (error) {
    notify('Erreur lors de la suppression', 'danger')
  } finally {
    deletingBooking.value = false
  }
}

const approve = async (booking) => {
  if (!booking?.id) return
  closeActions()
  actionBookingId.value = booking.id
  actionType.value = 'approve'
  try {
    await api.patch(`bookings/${booking.id}/`, { status: 'confirmed' })
    notify(`Réservation de ${booking.customer_name} approuvée`, 'success')
    fetchBookings()
  } catch (error) {
    notify('Erreur lors de l\'approbation', 'danger')
  } finally {
    actionBookingId.value = null
    actionType.value = ''
  }
}

const reject = async (booking) => {
  if (!booking?.id) return
  closeActions()
  actionBookingId.value = booking.id
  actionType.value = 'reject'
  try {
    await api.patch(`bookings/${booking.id}/`, { status: 'cancelled' })
    notify(`Réservation de ${booking.customer_name} rejetée`, 'warning')
    fetchBookings()
  } catch (error) {
    notify('Erreur lors du rejet', 'danger')
  } finally {
    actionBookingId.value = null
    actionType.value = ''
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
  form.value = { id: null, customer_name: '', customer_email: '', hall: halls.value[0]?.id || '', event_type: 'Mariage', event_type_other: '', start_date: '', end_date: '', total_price: 0, status: 'pending' }
  daysCount.value = 0
  showFormModal.value = true
}

const editBooking = (booking) => {
  closeActions()
  isEditing.value = true
  form.value = mapBookingToForm(booking)
  calculatePrice()
  showFormModal.value = true
}

const viewBooking = (booking) => {
  closeActions()
  selectedBooking.value = booking
  showViewModal.value = true
}

const confirmDelete = (booking) => {
  closeActions()
  selectedBooking.value = booking
  showDeleteModal.value = true
}

const normalizeEventType = (eventType, eventTypeOther = '') => {
  if (eventType !== 'Autres') return eventType
  const details = String(eventTypeOther || '').trim()
  return details ? `Autres: ${details}` : 'Autres'
}

const mapBookingToForm = (booking) => {
  const rawEventType = String(booking?.event_type || '')
  const isKnown = eventTypeOptions.includes(rawEventType)
  if (isKnown) {
    return { ...booking, event_type_other: '' }
  }

  const otherPrefix = 'Autres: '
  return {
    ...booking,
    event_type: 'Autres',
    event_type_other: rawEventType.startsWith(otherPrefix) ? rawEventType.slice(otherPrefix.length) : rawEventType,
  }
}

const buildBookingPayload = () => ({
  ...form.value,
  event_type: normalizeEventType(form.value.event_type, form.value.event_type_other),
})
</script>

<style scoped>
.bookings-page {
  padding: 0;
}

.admin-cards {
  width: 100%;
  max-width: 100%;
  overflow-x: hidden;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--space-10);
  gap: var(--space-4);
  flex-wrap: wrap;
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
  display: inline-flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: flex-end;
  gap: .5rem;
}

.controls-top {
  width: 100%;
  display: flex;
  gap: var(--space-3);
  align-items: center;
}

.filters-panel {
  width: 100%;
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-4);
  margin-top: var(--space-4);
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

.actions-dropdown {
  position: relative;
  display: inline-flex;
}

.actions-menu {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  min-width: 200px;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  box-shadow: 0 14px 35px rgba(15, 23, 42, 0.12);
  padding: 6px;
  z-index: 30;
}

.actions-item {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 10px;
  color: #334155;
  font-weight: 700;
  font-size: 0.9rem;
  text-align: left;
}

.actions-item:hover {
  background: #f8fafc;
  color: #0f172a;
}

.actions-item:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.actions-item.danger {
  color: #dc2626;
}

.actions-item.danger:hover {
  background: #fef2f2;
  color: #b91c1c;
}

@media (max-width: 992px) {
  .filters-toggle {
    display: inline-flex;
    align-items: center;
    justify-content: center;
  }

  .filters-panel {
    gap: var(--space-3);
  }
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
</style>
