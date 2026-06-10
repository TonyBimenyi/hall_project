<template>
  <div class="admin-expenses">
    <div class="header-actions">
      <h1>Suivi des Dépenses Internes</h1>
      <div class="header-buttons">
        <button class="btn btn-export btn-sm" :class="{ 'is-loading': exportingPdf }" :disabled="exportingPdf || exportingXls" @click="exportPdf">
          <i class="fas fa-file-pdf"></i> Export PDF
        </button>
        <button class="btn btn-export btn-sm" :class="{ 'is-loading': exportingXls }" :disabled="exportingPdf || exportingXls" @click="exportXls">
          <i class="fas fa-file-excel"></i> Export XLS
        </button>
        <button class="btn btn-primary btn-sm" @click="openAddModal">
          <i class="fas fa-plus"></i> Enregistrer une dépense
        </button>
      </div>
    </div>

    <div class="stats-grid mb-8">
      <div class="stat-card card">
        <div class="stat-icon danger"><i class="fas fa-money-bill-wave"></i></div>
        <div class="stat-info">
          <span class="stat-label">Total ce mois</span>
          <span class="stat-value">
            <span v-if="loadingExpenses" class="skeleton-line skeleton-w-60"></span>
            <template v-else>{{ formatMoney(displayTotalMonthlyExpenses) }}</template>
          </span>
        </div>
      </div>
      <div class="stat-card card">
        <div class="stat-icon info"><i class="fas fa-tools"></i></div>
        <div class="stat-info">
          <span class="stat-label">Maintenance</span>
          <span class="stat-value">
            <span v-if="loadingExpenses" class="skeleton-line skeleton-w-50"></span>
            <template v-else>{{ formatMoney(displayMaintenanceTotal) }}</template>
          </span>
        </div>
      </div>
      <div class="stat-card card">
        <div class="stat-icon primary"><i class="fas fa-shopping-cart"></i></div>
        <div class="stat-info">
          <span class="stat-label">Achats Matériel</span>
          <span class="stat-value">
            <span v-if="loadingExpenses" class="skeleton-line skeleton-w-50"></span>
            <template v-else>{{ formatMoney(displayEquipmentTotal) }}</template>
          </span>
        </div>
      </div>
      <div class="stat-card card">
        <div class="stat-icon success"><i class="fas fa-user-tie"></i></div>
        <div class="stat-info">
          <span class="stat-label">Salaires</span>
          <span class="stat-value">
            <span v-if="loadingExpenses" class="skeleton-line skeleton-w-50"></span>
            <template v-else>{{ formatMoney(displaySalariesTotal) }}</template>
          </span>
        </div>
      </div>
    </div>

    <div class="controls card">
      <div class="controls-top">
        <div class="search-wrapper">
          <i class="fas fa-search search-icon"></i>
          <input
            type="text"
            v-model="search"
            placeholder="Rechercher (description, bénéficiaire, payé par)..."
            class="search-input-clean"
          />
        </div>
        <button class="btn-icon filters-toggle" :class="{ active: filtersOpen }" title="Filtres" @click="filtersOpen = !filtersOpen">
          <i class="fas fa-filter"></i>
        </button>
      </div>
      <div v-show="!isMobile || filtersOpen" class="filters-panel">
        <select v-model="categoryFilter" class="filter-select-clean">
          <option value="">Toutes les catégories</option>
          <option value="Maintenance">Maintenance</option>
          <option value="Équipement">Équipement</option>
          <option value="Salaires">Salaires</option>
          <option value="Fournitures">Fournitures</option>
          <option value="Utilités">Utilités</option>
          <option value="Autre">Autre</option>
        </select>
        <select v-model="statusFilter" class="filter-select-clean">
          <option value="">Tous les statuts</option>
          <option value="paid">Payé</option>
          <option value="pending">En attente</option>
        </select>
        <input v-model="dateFrom" type="date" class="filter-input-clean" />
        <input v-model="dateTo" type="date" class="filter-input-clean" />
      </div>
    </div>

    <div class="table-container card">
      <div style="display:flex; align-items:center; justify-content:flex-end; gap:12px; flex-wrap:wrap; margin-bottom: var(--space-4);">
        <AdminAppTablePagination
          :start="expensesStartIndex"
          :end="expensesEndIndex"
          :total="expensesTotalItems"
          :can-prev="expensesCanPrev"
          :can-next="expensesCanNext"
          :disabled="loadingExpenses"
          @prev="expensesPrevPage"
          @next="expensesNextPage"
        />
      </div>
      <div v-if="isMobile" class="admin-cards">
        <template v-if="loadingExpenses">
          <div v-for="n in 6" :key="`sk-card-${n}`" class="admin-card">
            <div class="admin-card-head">
              <div style="width: 100%;">
                <div class="skeleton-line skeleton-w-70"></div>
                <div style="margin-top: 8px;" class="skeleton-line skeleton-w-50"></div>
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
          <div v-for="expense in paginatedExpenses" :key="expense.id" class="admin-card">
            <div class="admin-card-head">
              <div>
                <div class="admin-card-title">{{ expense.description }}</div>
                <div class="admin-card-subtitle">{{ expense.date }} • {{ expense.category }}</div>
              </div>

              <div class="actions-dropdown">
                <button class="btn-icon details" title="Détails" @click.stop="toggleActions(expense.id)">
                  <i class="fas fa-ellipsis-vertical"></i>
                </button>
                <div v-if="openActionsId === expense.id" class="actions-menu" @click.stop>
                  <button class="actions-item" @click="viewExpense(expense)">
                    <i class="fas fa-eye"></i> Voir
                  </button>
                  <button class="actions-item" @click="editExpense(expense)">
                    <i class="fas fa-edit"></i> Modifier
                  </button>
                  <button class="actions-item danger" @click="confirmDelete(expense)">
                    <i class="fas fa-trash-alt"></i> Supprimer
                  </button>
                </div>
              </div>
            </div>

            <div class="admin-card-body">
              <div class="admin-kv">
                <span class="k">Montant</span>
                <span class="v">{{ formatMoney(expense.amount) }}</span>
              </div>
              <div class="admin-kv">
                <span class="k">Payé par</span>
                <span class="v">{{ expense.paid_by }}</span>
              </div>
              <div class="admin-kv">
                <span class="k">Statut</span>
                <span class="v">
                  <span :class="['badge', expense.status === 'paid' ? 'badge-success' : 'badge-warning']">
                    {{ translateStatus(expense.status) }}
                  </span>
                </span>
              </div>
            </div>
          </div>
        </template>
        <div v-if="!loadingExpenses && filteredExpenses.length === 0" class="empty-cell">Aucune dépense</div>
      </div>

      <table v-else ref="tableRef" class="admin-table">
        <thead>
          <tr>
            <th>Date</th>
            <th>Description</th>
            <th>Catégorie</th>
            <th>Montant</th>
            <th>Payé par</th>
            <th>Statut</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <template v-if="loadingExpenses">
            <tr v-for="n in 6" :key="`sk-${n}`">
              <td><div class="skeleton-line skeleton-w-40"></div></td>
              <td><div class="skeleton-line skeleton-w-80"></div></td>
              <td><div class="skeleton-line skeleton-w-50"></div></td>
              <td><div class="skeleton-line skeleton-w-40"></div></td>
              <td><div class="skeleton-line skeleton-w-50"></div></td>
              <td><div class="skeleton-line skeleton-w-30"></div></td>
              <td><div class="skeleton-line skeleton-w-60"></div></td>
            </tr>
          </template>
          <tr v-else v-for="expense in paginatedExpenses" :key="expense.id">
            <td>{{ expense.date }}</td>
            <td><strong>{{ expense.description }}</strong></td>
            <td>{{ expense.category }}</td>
            <td>{{ formatMoney(expense.amount) }}</td>
            <td>{{ expense.paid_by }}</td>
            <td>
              <span :class="['badge', expense.status === 'paid' ? 'badge-success' : 'badge-warning']">
                {{ translateStatus(expense.status) }}
              </span>
            </td>
            <td class="actions-cell">
              <div class="actions-dropdown">
                <button class="btn-icon details" title="Détails" @click.stop="toggleActions(expense.id)">
                  <i class="fas fa-ellipsis-vertical"></i>
                </button>
                <div v-if="openActionsId === expense.id" class="actions-menu" @click.stop>
                  <button class="actions-item" @click="viewExpense(expense)">
                    <i class="fas fa-eye"></i> Voir
                  </button>
                  <button class="actions-item" @click="editExpense(expense)">
                    <i class="fas fa-edit"></i> Modifier
                  </button>
                  <button class="actions-item danger" @click="confirmDelete(expense)">
                    <i class="fas fa-trash-alt"></i> Supprimer
                  </button>
                </div>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Add/Edit Modal -->
    <AdminAppModal v-model="showFormModal" :title="isEditing ? 'Modifier la dépense' : 'Enregistrer une dépense'" width="500px">
      <form @submit.prevent="saveExpense" class="admin-form">
        <div class="form-group">
          <label class="form-label">Description</label>
          <input v-model="form.description" type="text" class="form-input" required placeholder="Ex: Réparation climatisation" />
        </div>
        <div class="form-group">
          <label class="form-label">Catégorie</label>
          <select v-model="form.category" class="form-select" required>
            <option value="Maintenance">Maintenance</option>
            <option value="Équipement">Équipement</option>
            <option value="Salaires">Salaires</option>
            <option value="Fournitures">Fournitures</option>
            <option value="Utilités">Utilités</option>
            <option value="Autre">Autre</option>
          </select>
        </div>
        <div class="form-grid">
          <div class="form-group">
            <label class="form-label">Montant (Fbu)</label>
            <input v-model="amountInput" inputmode="numeric" type="text" class="form-input" placeholder="0" required />
          </div>
          <div class="form-group">
            <label class="form-label">Date</label>
            <input v-model="form.date" type="date" class="form-input" required />
          </div>
        </div>
        <div class="form-group">
          <label class="form-label">Bénéficiaire / Fournisseur</label>
          <input v-model="form.paid_to" type="text" class="form-input" required placeholder="Ex: SODECI, Agent de sécurité, etc." />
        </div>
        <div class="form-grid">
          <div class="form-group">
            <label class="form-label">Payé par</label>
            <input v-model="form.paid_by" type="text" class="form-input" required />
          </div>
          <div class="form-group">
            <label class="form-label">Statut</label>
            <select v-model="form.status" class="form-select" required>
              <option value="paid">Payé</option>
              <option value="pending">En attente</option>
            </select>
          </div>
        </div>
      </form>
      <template #footer>
        <button class="btn btn-outline" @click="showFormModal = false">Annuler</button>
        <button class="btn btn-primary" :class="{ 'is-loading': savingExpense }" :disabled="savingExpense" @click="saveExpense">
          {{ isEditing ? 'Mettre à jour' : 'Enregistrer' }}
        </button>
      </template>
    </AdminAppModal>

    <!-- View Modal -->
    <AdminAppModal v-model="showViewModal" title="Détails de la dépense" width="400px">
      <div v-if="selectedExpense" class="view-details">
        <div class="detail-item">
          <span class="detail-label">Description</span>
          <span class="detail-val">{{ selectedExpense.description }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">Catégorie</span>
          <span class="detail-val">{{ selectedExpense.category }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">Montant</span>
          <span class="detail-val">{{ formatMoney(selectedExpense.amount) }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">Date</span>
          <span class="detail-val">{{ selectedExpense.date }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">Bénéficiaire</span>
          <span class="detail-val">{{ selectedExpense.paid_to }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">Payé par</span>
          <span class="detail-val">{{ selectedExpense.paid_by }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">Statut</span>
          <span :class="['badge', selectedExpense.status === 'paid' ? 'badge-success' : 'badge-warning']">
            {{ translateStatus(selectedExpense.status) }}
          </span>
        </div>
      </div>
      <template #footer>
        <button class="btn btn-primary" @click="showViewModal = false">Fermer</button>
      </template>
    </AdminAppModal>

    <!-- Delete Confirmation Modal -->
    <AdminAppModal v-model="showDeleteModal" title="Confirmer la suppression" width="400px">
      <p>Êtes-vous sûr de vouloir supprimer cette dépense : <strong>{{ selectedExpense?.description }}</strong> ?</p>
      <template #footer>
        <button class="btn btn-outline" @click="showDeleteModal = false">Annuler</button>
        <button class="btn btn-danger" :class="{ 'is-loading': deletingExpense }" :disabled="deletingExpense" @click="deleteExpense">
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

definePageMeta({ layout: 'admin' })
const { formatMoney, moneyInputModel } = useMoney()

const expenses = ref([])
const tableRef = ref(null)
const exportingPdf = ref(false)
const exportingXls = ref(false)
const search = ref('')
const categoryFilter = ref('')
const statusFilter = ref('')
const dateFrom = ref('')
const dateTo = ref('')
const loadingExpenses = ref(false)
const isMobile = ref(false)
const filtersOpen = ref(false)
const openActionsId = ref(null)
const savingExpense = ref(false)
const deletingExpense = ref(false)

const toggleActions = (id) => {
  openActionsId.value = openActionsId.value === id ? null : id
}

const closeActions = () => {
  openActionsId.value = null
}

const exportXls = async () => {
  if (!tableRef.value) return
  exportingXls.value = true
  await nextTick()
  const html = `<!doctype html><html><head><meta charset="utf-8"></head><body>${tableRef.value.outerHTML}</body></html>`
  const blob = new Blob([html], { type: 'application/vnd.ms-excel' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'expenses.xls'
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
  win.document.write(`<!doctype html><html><head><meta charset="utf-8"><title>Dépenses</title><style>
  body{font-family:Arial, sans-serif; padding:20px}
  table{width:100%; border-collapse:collapse}
  th,td{border:1px solid #e2e8f0; padding:8px; text-align:left; font-size:12px}
  th{background:#f8fafc}
  </style></head><body><h2>Dépenses</h2>${tableRef.value.outerHTML}</body></html>`)
  win.document.close()
  win.focus()
  win.print()
  win.close()
  setTimeout(() => {
    exportingPdf.value = false
  }, 350)
}

const fetchExpenses = async () => {
  loadingExpenses.value = true
  try {
    const response = await api.get('expenses/')
    expenses.value = response.data
  } catch (error) {
    notify('Erreur lors du chargement des dépenses', 'danger')
  } finally {
    loadingExpenses.value = false
  }
}

onMounted(() => {
  fetchExpenses()
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

const totalMonthlyExpenses = computed(() => expenses.value.reduce((acc, exp) => acc + parseFloat(exp.amount), 0))
const maintenanceTotal = computed(() => expenses.value.filter(e => e.category === 'Maintenance').reduce((acc, exp) => acc + parseFloat(exp.amount), 0))
const equipmentTotal = computed(() => expenses.value.filter(e => e.category === 'Équipement').reduce((acc, exp) => acc + parseFloat(exp.amount), 0))
const salariesTotal = computed(() => expenses.value.filter(e => e.category === 'Salaires').reduce((acc, exp) => acc + parseFloat(exp.amount), 0))

const displayTotalMonthlyExpenses = ref(0)
const displayMaintenanceTotal = ref(0)
const displayEquipmentTotal = ref(0)
const displaySalariesTotal = ref(0)

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

watch(totalMonthlyExpenses, (v) => animateCounter(displayTotalMonthlyExpenses, v), { immediate: true })
watch(maintenanceTotal, (v) => animateCounter(displayMaintenanceTotal, v), { immediate: true })
watch(equipmentTotal, (v) => animateCounter(displayEquipmentTotal, v), { immediate: true })
watch(salariesTotal, (v) => animateCounter(displaySalariesTotal, v), { immediate: true })

onBeforeUnmount(() => {
  for (const id of rafMap.values()) cancelAnimationFrame(id)
})

const filteredExpenses = computed(() => {
  const q = search.value.toLowerCase().trim()
  return (expenses.value || []).filter((e) => {
    const matchesSearch = q === '' ||
      String(e.description || '').toLowerCase().includes(q) ||
      String(e.paid_to || '').toLowerCase().includes(q) ||
      String(e.paid_by || '').toLowerCase().includes(q)
    const matchesCategory = categoryFilter.value === '' || e.category === categoryFilter.value
    const matchesStatus = statusFilter.value === '' || e.status === statusFilter.value
    const date = e.date ? new Date(e.date) : null
    const fromOk = !dateFrom.value || (date && date >= new Date(dateFrom.value))
    const toOk = !dateTo.value || (date && date <= new Date(dateTo.value))
    return matchesSearch && matchesCategory && matchesStatus && fromOk && toOk
  })
})

const {
  paginatedItems: paginatedExpenses,
  totalItems: expensesTotalItems,
  startIndex: expensesStartIndex,
  endIndex: expensesEndIndex,
  canPrev: expensesCanPrev,
  canNext: expensesCanNext,
  prevPage: expensesPrevPage,
  nextPage: expensesNextPage,
} = usePagination(filteredExpenses, 50)

const showFormModal = ref(false)
const showViewModal = ref(false)
const showDeleteModal = ref(false)
const isEditing = ref(false)
const selectedExpense = ref(null)

const form = ref({
  id: null,
  date: '',
  description: '',
  category: 'Autre',
  amount: 0,
  paid_by: 'Admin',
  paid_to: '',
  status: 'paid'
})
const amountInput = moneyInputModel(form, 'amount')

const resetForm = () => {
  form.value = {
    id: null,
    date: new Date().toISOString().split('T')[0],
    description: '',
    category: 'Autre',
    amount: 0,
    paid_by: 'Admin',
    paid_to: '',
    status: 'paid'
  }
}

const openAddModal = () => {
  isEditing.value = false
  resetForm()
  showFormModal.value = true
}

const viewExpense = (expense) => {
  closeActions()
  selectedExpense.value = expense
  showViewModal.value = true
}

const editExpense = (expense) => {
  closeActions()
  isEditing.value = true
  form.value = { ...expense }
  showFormModal.value = true
}

const confirmDelete = (expense) => {
  closeActions()
  selectedExpense.value = expense
  showDeleteModal.value = true
}

const saveExpense = async () => {
  if (savingExpense.value) return
  savingExpense.value = true
  try {
    if (isEditing.value) {
      await api.put(`expenses/${form.value.id}/`, form.value)
      notify('Dépense mise à jour avec succès')
    } else {
      await api.post('expenses/', form.value)
      notify('Dépense enregistrée avec succès')
    }
    showFormModal.value = false
    fetchExpenses()
  } catch (error) {
    notify('Erreur lors de l\'enregistrement', 'danger')
  } finally {
    savingExpense.value = false
  }
}

const deleteExpense = async () => {
  if (deletingExpense.value || !selectedExpense.value?.id) return
  deletingExpense.value = true
  try {
    await api.delete(`expenses/${selectedExpense.value.id}/`)
    notify('Dépense supprimée', 'danger')
    showDeleteModal.value = false
    fetchExpenses()
  } catch (error) {
    notify('Erreur lors de la suppression', 'danger')
  } finally {
    deletingExpense.value = false
  }
}

const translateStatus = (status) => {
  const map = {
    paid: 'Payé',
    pending: 'En attente'
  }
  return map[status] || status
}
</script>

<style scoped>
.admin-expenses {
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

.header-buttons {
  display: inline-flex;
  gap: .5rem;
  align-items: center;
  flex-wrap: wrap;
}

.controls {
  display: flex;
  gap: var(--space-4);
  margin-bottom: var(--space-8);
  padding: var(--space-4) var(--space-6);
  align-items: center;
  flex-wrap: wrap;
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
  gap: var(--space-4);
  flex-wrap: wrap;
  align-items: center;
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

.actions-cell {
  width: 1%;
  white-space: nowrap;
}

.actions-dropdown {
  position: relative;
  display: inline-flex;
}

.actions-menu {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  min-width: 190px;
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

.actions-item.danger {
  color: #dc2626;
}

.actions-item.danger:hover {
  background: #fef2f2;
  color: #b91c1c;
}

.filters-panel .filter-select-clean,
.filters-panel .filter-input-clean {
  flex: 1 1 190px;
}

.search-wrapper {
  flex: 1 1 360px;
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

.header-actions h1 {
  font-size: 1.75rem;
  font-weight: 800;
  color: #0f172a;
  margin-bottom: 0;
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

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: var(--space-6);
  margin-bottom: var(--space-10);
}

.stat-card {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-6);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
}

.stat-icon.danger { background: #fef2f2; color: #ef4444; }
.stat-icon.info { background: #f0f9ff; color: #0ea5e9; }
.stat-icon.primary { background: #f1f5f9; color: #0f172a; }
.stat-icon.success { background: #f0fdf4; color: #22c55e; }

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-label {
  display: block;
  font-size: 0.7rem;
  color: #94a3b8;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.125rem;
}

.stat-value {
  display: block;
  font-size: 1.25rem;
  font-weight: 800;
  color: #0f172a;
  line-height: 1.2;
}
</style>
