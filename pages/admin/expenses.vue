<template>
  <div class="admin-expenses">
    <div class="header-actions">
      <h1>Suivi des Dépenses Internes</h1>
      <div class="header-buttons">
        <button class="btn btn-export btn-sm admin-head-btn" :class="{ 'is-loading': exportingPdf }" :disabled="exportingPdf || exportingXls" @click="exportPdf">
          <i class="fas fa-file-pdf"></i>
          <span class="btn-label">Export PDF</span>
        </button>
        <button v-if="canExportExcel" class="btn btn-export btn-sm admin-head-btn" :class="{ 'is-loading': exportingXls }" :disabled="exportingPdf || exportingXls" @click="exportXls">
          <i class="fas fa-file-excel"></i>
          <span class="btn-label">Export XLS</span>
        </button>
        <button class="btn btn-primary btn-sm admin-head-btn" @click="openAddModal">
          <i class="fas fa-plus"></i>
          <span class="btn-label">Enregistrer une dépense</span>
        </button>
      </div>
    </div>

    <div v-if="canSeeExpenseStats" class="stats-grid mb-8">
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
        <button class="btn btn-sm" @click="resetFilters" style="margin-right: 8px;">
          <i class="fas fa-redo"></i> Réinitialiser
        </button>
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
        <select v-model="preset" class="filter-select-clean">
          <option value="7d">7 jours</option>
          <option value="28d">28 jours</option>
          <option value="90d">90 jours</option>
          <option value="this_month">Ce mois</option>
          <option value="last_month">Mois dernier</option>
          <option value="year">Cette année</option>
          <option value="custom">Personnalisé</option>
        </select>
        <input v-if="preset === 'custom'" v-model="customStart" type="date" class="filter-input-clean" />
        <input v-if="preset === 'custom'" v-model="customEnd" type="date" class="filter-input-clean" />
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
                <div class="admin-card-subtitle">{{ getExpenseDisplayId(expense) }} • {{ expense.date }} • {{ expense.category }}</div>
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
                <span class="k">ID</span>
                <span class="v">{{ getExpenseDisplayId(expense) }}</span>
              </div>
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
            <th><button class="table-sort-btn" :class="{ active: isExpenseSortActive('id') }" @click="toggleExpenseSort('id')">ID <i :class="expenseSortIconClass('id')"></i></button></th>
            <th><button class="table-sort-btn" :class="{ active: isExpenseSortActive('date') }" @click="toggleExpenseSort('date')">Date <i :class="expenseSortIconClass('date')"></i></button></th>
            <th><button class="table-sort-btn" :class="{ active: isExpenseSortActive('description') }" @click="toggleExpenseSort('description')">Description <i :class="expenseSortIconClass('description')"></i></button></th>
            <th><button class="table-sort-btn" :class="{ active: isExpenseSortActive('category') }" @click="toggleExpenseSort('category')">Catégorie <i :class="expenseSortIconClass('category')"></i></button></th>
            <th><button class="table-sort-btn" :class="{ active: isExpenseSortActive('amount') }" @click="toggleExpenseSort('amount')">Montant <i :class="expenseSortIconClass('amount')"></i></button></th>
            <th><button class="table-sort-btn" :class="{ active: isExpenseSortActive('paid_by') }" @click="toggleExpenseSort('paid_by')">Payé par <i :class="expenseSortIconClass('paid_by')"></i></button></th>
            <th><button class="table-sort-btn" :class="{ active: isExpenseSortActive('status') }" @click="toggleExpenseSort('status')">Statut <i :class="expenseSortIconClass('status')"></i></button></th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <template v-if="loadingExpenses">
            <tr v-for="n in 6" :key="`sk-${n}`">
              <td><div class="skeleton-line skeleton-w-40"></div></td>
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
            <td><code>{{ getExpenseDisplayId(expense) }}</code></td>
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
            <input v-model="form.paid_by" type="text" class="form-input" required readonly />
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
    <AdminAppModal v-model="showViewModal" title="Détails de la dépense" width="580px">
      <div v-if="selectedExpense" class="entity-view-modal">
        <div class="entity-view-hero">
          <div class="entity-view-avatar">{{ String(getExpenseDisplayId(selectedExpense) || 'DE').slice(0, 2).toUpperCase() }}</div>
          <div class="entity-view-main">
            <div class="entity-view-code">{{ getExpenseDisplayId(selectedExpense) }}</div>
            <h3>{{ selectedExpense.description }}</h3>
            <p>{{ selectedExpense.category }}</p>
          </div>
          <div class="entity-view-badges">
            <span :class="['badge', selectedExpense.status === 'paid' ? 'badge-success' : 'badge-warning']">{{ translateStatus(selectedExpense.status) }}</span>
            <span class="badge badge-info">{{ formatMoney(selectedExpense.amount) }}</span>
          </div>
        </div>

        <div class="entity-view-grid">
          <section class="entity-view-card">
            <div class="entity-view-card-title">Dépense</div>
            <div class="entity-view-list">
              <div class="entity-view-item"><span class="entity-view-label">Catégorie</span><span class="entity-view-value">{{ selectedExpense.category }}</span></div>
              <div class="entity-view-item"><span class="entity-view-label">Date</span><span class="entity-view-value">{{ selectedExpense.date }}</span></div>
              <div class="entity-view-item"><span class="entity-view-label">Bénéficiaire</span><span class="entity-view-value">{{ selectedExpense.paid_to }}</span></div>
              <div class="entity-view-item"><span class="entity-view-label">Payé par</span><span class="entity-view-value">{{ selectedExpense.paid_by }}</span></div>
              <div class="entity-view-item"><span class="entity-view-label">Montant</span><span class="entity-view-value">{{ formatMoney(selectedExpense.amount) }}</span></div>
            </div>
          </section>

          <section class="entity-view-card">
            <div class="entity-view-card-title">Suivi administratif</div>
            <div class="entity-view-list">
              <div class="entity-view-item"><span class="entity-view-label">Référence</span><span class="entity-view-value">{{ getExpenseDisplayId(selectedExpense) }}</span></div>
              <div class="entity-view-item"><span class="entity-view-label">Statut</span><span class="entity-view-value">{{ translateStatus(selectedExpense.status) }}</span></div>
              <div class="entity-view-item"><span class="entity-view-label">Créé le</span><span class="entity-view-value">{{ formatDisplayDate(selectedExpense.created_at) }}</span></div>
              <div class="entity-view-item"><span class="entity-view-label">Créé par</span><span class="entity-view-value">{{ selectedExpense.created_by_name || '-' }}</span></div>
              <div class="entity-view-item"><span class="entity-view-label">Dernière action</span><span class="entity-view-value">{{ selectedExpense.updated_by_name || selectedExpense.created_by_name || '-' }}</span></div>
            </div>
          </section>
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
import { useDateFormat } from '~/composables/useDateFormat'
import { usePagination } from '~/composables/usePagination'
import { useDisplayIds } from '~/composables/useDisplayIds'
import { useTableSort } from '~/composables/useTableSort'
import { useAdminExportDocuments } from '~/composables/useAdminExportDocuments'
import { canExportAdminExcel, canSeeSyntheticRevenue, getRoleKey, getStoredUser } from '~/composables/useRoleAccess'

definePageMeta({ layout: 'admin' })
const { formatMoney, moneyInputModel } = useMoney()
const { buildHashSequenceMap } = useDisplayIds()
const { getSanitizedExportHtml, buildPdfDocumentHtml, downloadHtmlAsXls, downloadPdfHtml, buildExportFileName } = useAdminExportDocuments()

const expenses = ref([])
const currentUser = ref({})
const tableRef = ref(null)
const exportingPdf = ref(false)
const exportingXls = ref(false)
const search = ref('')
const categoryFilter = ref('')
const statusFilter = ref('')
const preset = ref('28d')
const customStart = ref('')
const customEnd = ref('')

const toYmd = (date) => {
  const d = (date instanceof Date) ? date : new Date(date)
  if (Number.isNaN(d.getTime())) return ''
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

const addDays = (ymd, days) => {
  const base = new Date(`${ymd}T00:00:00`)
  base.setDate(base.getDate() + days)
  return toYmd(base)
}

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

const inRangeYmd = (ymd, rangeStart, rangeEnd) => {
  const v = String(ymd || '').slice(0, 10)
  if (!v || !rangeStart || !rangeEnd) return false
  return v >= rangeStart && v <= rangeEnd
}
const loadingExpenses = ref(false)
const isMobile = ref(false)
const filtersOpen = ref(false)
const openActionsId = ref(null)
const savingExpense = ref(false)
const deletingExpense = ref(false)
const canExportExcel = computed(() => canExportAdminExcel(currentUser.value))
const canSeeExpenseStats = computed(() => canSeeSyntheticRevenue(currentUser.value))
const isReceptionist = computed(() => getRoleKey(currentUser.value) === 'receptionniste')
const currentUserId = computed(() => Number(currentUser.value?.id || currentUser.value?.user_id || 0))
const currentExpenseUserLabel = computed(() => (
  String(
    currentUser.value?.username ||
    currentUser.value?.full_name ||
    currentUser.value?.name ||
    currentUser.value?.email ||
    'Utilisateur connecté'
  ).trim() || 'Utilisateur connecté'
))

const toggleActions = (id) => {
  openActionsId.value = openActionsId.value === id ? null : id
}

const closeActions = () => {
  openActionsId.value = null
}

const resetFilters = () => {
  search.value = ''
  categoryFilter.value = ''
  statusFilter.value = ''
  preset.value = '28d'
  customStart.value = ''
  customEnd.value = ''
}

const exportXls = async () => {
  if (!canExportExcel.value) {
    notify("L'export Excel n'est pas autorisé pour ce rôle", 'warning')
    return
  }
  if (!tableRef.value) return
  exportingXls.value = true
  await nextTick()
  const contentHtml = getSanitizedExportHtml(tableRef.value, { htmlMode: 'outer', removeActionsColumn: true })
  downloadHtmlAsXls({ type: 'expenses', contentHtml })
  setTimeout(() => {
    exportingXls.value = false
  }, 350)
}

const exportPdf = async () => {
  if (!tableRef.value) return
  exportingPdf.value = true
  await nextTick()
  const contentHtml = getSanitizedExportHtml(tableRef.value, { htmlMode: 'outer', removeActionsColumn: true })
  const html = buildPdfDocumentHtml({
    title: 'Dépenses',
    documentTitle: buildExportFileName('expenses', 'pdf').replace(/\.pdf$/, ''),
    subtitle: 'Liste des dépenses filtrées exportée depuis l’administration.',
    typeLabel: 'Dépenses PDF',
    tableTitle: 'Liste des dépenses',
    periodLabel: rangeStartYmd.value && rangeEndYmd.value ? `${rangeStartYmd.value} -> ${rangeEndYmd.value}` : 'Toutes les dates',
    contentHtml,
  })
  const ok = await downloadPdfHtml({ html, fileName: buildExportFileName('expenses', 'pdf') })
  if (!ok) {
    exportingPdf.value = false
    return
  }
  setTimeout(() => {
    exportingPdf.value = false
  }, 350)
}

const fetchExpenses = async () => {
  loadingExpenses.value = true
  try {
    const response = await api.get('expenses/')
    expenses.value = Array.isArray(response.data) ? response.data : []
  } catch (error) {
    notify('Erreur lors du chargement des dépenses', 'danger')
  } finally {
    loadingExpenses.value = false
  }
}

onMounted(() => {
  currentUser.value = getStoredUser()
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
    const matchesOwnership = !isReceptionist.value || Number(e?.created_by || 0) === currentUserId.value
    const matchesSearch = q === '' ||
      String(e.description || '').toLowerCase().includes(q) ||
      String(e.paid_to || '').toLowerCase().includes(q) ||
      String(e.paid_by || '').toLowerCase().includes(q)
    const matchesCategory = categoryFilter.value === '' || e.category === categoryFilter.value
    const matchesStatus = statusFilter.value === '' || e.status === statusFilter.value
    const matchesDate = inRangeYmd(e.date, rangeStartYmd.value, rangeEndYmd.value)
    return matchesOwnership && matchesSearch && matchesCategory && matchesStatus && matchesDate
  })
})

const {
  sortedItems: sortedExpenses,
  toggleSort: toggleExpenseSort,
  isSortActive: isExpenseSortActive,
  sortIconClass: expenseSortIconClass,
} = useTableSort(filteredExpenses, {
  initialKey: 'id',
  initialDirection: 'desc',
  accessors: {
    amount: expense => Number(expense?.amount || 0),
  },
})

const expenseDisplayIds = computed(() => buildHashSequenceMap(expenses.value))
const getExpenseDisplayId = (expense) => expenseDisplayIds.value.get(expense?.id) || '#0001'

const {
  paginatedItems: paginatedExpenses,
  totalItems: expensesTotalItems,
  startIndex: expensesStartIndex,
  endIndex: expensesEndIndex,
  canPrev: expensesCanPrev,
  canNext: expensesCanNext,
  prevPage: expensesPrevPage,
  nextPage: expensesNextPage,
} = usePagination(sortedExpenses, 50)

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
  paid_by: '',
  paid_to: '',
  status: 'paid'
})
const amountInput = moneyInputModel(form, 'amount')
const { formatDisplayDate } = useDateFormat()

const resetForm = () => {
  form.value = {
    id: null,
    date: new Date().toISOString().split('T')[0],
    description: '',
    category: 'Autre',
    amount: 0,
    paid_by: currentExpenseUserLabel.value,
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
  form.value = {
    ...expense,
    paid_by: currentExpenseUserLabel.value,
  }
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
    form.value.paid_by = currentExpenseUserLabel.value
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

.entity-view-modal { display: grid; gap: 18px; }
.entity-view-hero { display: flex; align-items: center; gap: 16px; padding: 18px; border-radius: 20px; background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); color: #ffffff; }
.entity-view-avatar { width: 64px; height: 64px; border-radius: 18px; background: rgba(255,255,255,.14); border: 1px solid rgba(255,255,255,.18); display: flex; align-items: center; justify-content: center; font-size: 1rem; font-weight: 800; letter-spacing: .08em; flex-shrink: 0; }
.entity-view-main { min-width: 0; flex: 1; }
.entity-view-code { display: inline-flex; align-items: center; padding: 6px 10px; border-radius: 999px; background: rgba(255,255,255,.14); font-size: .72rem; font-weight: 800; letter-spacing: .08em; text-transform: uppercase; }
.entity-view-main h3 { margin: 6px 0 4px; font-size: 1.15rem; font-weight: 800; color: #ffffff; }
.entity-view-main p { margin: 0; color: rgba(255,255,255,.78); font-size: .92rem; }
.entity-view-badges { display: flex; flex-direction: column; align-items: flex-end; gap: 8px; }
.entity-view-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; }
.entity-view-card { border: 1px solid #e2e8f0; border-radius: 18px; background: #ffffff; padding: 16px; }
.entity-view-card-title { margin-bottom: 14px; font-size: .78rem; font-weight: 800; letter-spacing: .08em; text-transform: uppercase; color: #64748b; }
.entity-view-list { display: grid; gap: 10px; }
.entity-view-item { display: flex; justify-content: space-between; gap: 12px; padding: 10px 12px; border-radius: 14px; background: #f8fafc; border: 1px solid #e2e8f0; }
.entity-view-label { color: #64748b; font-size: .82rem; font-weight: 700; }
.entity-view-value { color: #0f172a; font-size: .9rem; font-weight: 700; text-align: right; word-break: break-word; }

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

@media (max-width: 640px) {
  .entity-view-hero { flex-direction: column; align-items: flex-start; }
  .entity-view-badges { align-items: flex-start; flex-direction: row; flex-wrap: wrap; }
  .entity-view-grid { grid-template-columns: 1fr; }
  .entity-view-item { flex-direction: column; }
  .entity-view-value { text-align: left; }
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
