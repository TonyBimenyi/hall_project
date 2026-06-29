<template>
  <div class="admin-entrees">
    <div class="page-header">
      <div>
        <h1>Entrees</h1>
        <p>Enregistrer les recettes manuelles pour les integrer automatiquement dans la comptabilite.</p>
      </div>
      <div class="header-actions">
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
          <span class="btn-label">Nouvelle entree</span>
        </button>
      </div>
    </div>

    <div class="stats-grid mb-8">
      <div class="stat-card card">
        <div class="stat-icon success"><i class="fas fa-arrow-trend-up"></i></div>
        <div class="stat-info">
          <span class="stat-label">Valide ce mois</span>
          <span class="stat-value">{{ formatMoney(totalMonthlyPaid) }}</span>
        </div>
      </div>
      <div class="stat-card card">
        <div class="stat-icon info"><i class="fas fa-wallet"></i></div>
        <div class="stat-info">
          <span class="stat-label">Recettes validees</span>
          <span class="stat-value">{{ formatMoney(totalPaidEntrees) }}</span>
        </div>
      </div>
      <div class="stat-card card">
        <div class="stat-icon warning"><i class="fas fa-clock"></i></div>
        <div class="stat-info">
          <span class="stat-label">En attente</span>
          <span class="stat-value">{{ formatMoney(totalPendingEntrees) }}</span>
        </div>
      </div>
      <div class="stat-card card">
        <div class="stat-icon primary"><i class="fas fa-receipt"></i></div>
        <div class="stat-info">
          <span class="stat-label">Nombre d'entrees</span>
          <span class="stat-value">{{ entrees.length }}</span>
        </div>
      </div>
    </div>

    <div class="controls card">
      <div class="controls-top">
        <div class="search-wrapper">
          <i class="fas fa-search search-icon"></i>
          <input
            v-model="search"
            type="text"
            class="search-input-clean"
            placeholder="Rechercher par reference, intitule, provenance ou recu par..."
          />
        </div>
        <button class="btn btn-sm" @click="resetFilters">
          <i class="fas fa-redo"></i> Reinitialiser
        </button>
        <button class="btn-icon filters-toggle" :class="{ active: filtersOpen }" title="Filtres" @click="filtersOpen = !filtersOpen">
          <i class="fas fa-filter"></i>
        </button>
      </div>
      <div v-show="!isMobile || filtersOpen" class="filters-panel">
        <select v-model="categoryFilter" class="filter-select-clean">
          <option value="">Toutes les categories</option>
          <option v-for="category in categories" :key="category" :value="category">{{ category }}</option>
        </select>
        <select v-model="statusFilter" class="filter-select-clean">
          <option value="">Tous les statuts</option>
          <option value="paid">Validee</option>
          <option value="pending">En attente</option>
        </select>
        <select v-model="preset" class="filter-select-clean">
          <option value="7d">7 jours</option>
          <option value="28d">28 jours</option>
          <option value="90d">90 jours</option>
          <option value="this_month">Ce mois</option>
          <option value="last_month">Mois dernier</option>
          <option value="year">Cette annee</option>
          <option value="all">Toutes les dates</option>
          <option value="custom">Personnalise</option>
        </select>
        <input v-if="preset === 'custom'" v-model="customStart" type="date" class="filter-input-clean" />
        <input v-if="preset === 'custom'" v-model="customEnd" type="date" class="filter-input-clean" />
      </div>
    </div>

    <div ref="exportRef" class="table-container card">
      <div class="table-topbar">
        <div>
          <h2>Journal des entrees</h2>
          <p>Les entrees validees alimentent automatiquement les recettes de la comptabilite.</p>
        </div>
        <AdminAppTablePagination
          :start="entreesStartIndex"
          :end="entreesEndIndex"
          :total="entreesTotalItems"
          :can-prev="entreesCanPrev"
          :can-next="entreesCanNext"
          :disabled="loadingEntrees"
          @prev="entreesPrevPage"
          @next="entreesNextPage"
        />
      </div>

      <div v-if="isMobile" class="admin-cards">
        <template v-if="loadingEntrees">
          <div v-for="n in 5" :key="`entree-sk-${n}`" class="admin-card">
            <div class="admin-card-head">
              <div style="width: 100%;">
                <div class="skeleton-line skeleton-w-70"></div>
                <div style="margin-top: 8px;" class="skeleton-line skeleton-w-50"></div>
              </div>
            </div>
            <div class="admin-card-body">
              <div class="skeleton-line skeleton-w-60"></div>
              <div class="skeleton-line skeleton-w-40"></div>
            </div>
          </div>
        </template>
        <template v-else>
          <div v-for="entree in paginatedEntrees" :key="entree.id" class="admin-card has-actions">
            <div class="admin-card-head">
              <div>
                <div class="admin-card-title">{{ entree.title }}</div>
                <div class="admin-card-subtitle">{{ getEntreeDisplayId(entree) }} • {{ entree.reference }} • {{ entree.date }}</div>
              </div>
              <div class="actions-dropdown">
                <button class="btn-icon details" title="Actions" @click.stop="toggleActions(entree.id)">
                  <i class="fas fa-ellipsis-vertical"></i>
                </button>
                <div v-if="openActionsId === entree.id" class="actions-menu" @click.stop>
                  <button class="actions-item" @click="viewEntree(entree)">
                    <i class="fas fa-eye"></i> Voir
                  </button>
                  <button class="actions-item" @click="editEntree(entree)">
                    <i class="fas fa-edit"></i> Modifier
                  </button>
                  <button class="actions-item danger" @click="confirmDelete(entree)">
                    <i class="fas fa-trash-alt"></i> Supprimer
                  </button>
                </div>
              </div>
            </div>
            <div class="admin-card-body">
              <div class="admin-kv"><span class="k">Categorie</span><span class="v">{{ entree.category || '-' }}</span></div>
              <div class="admin-kv"><span class="k">Recu de</span><span class="v">{{ entree.received_from || '-' }}</span></div>
              <div class="admin-kv"><span class="k">Recu par</span><span class="v">{{ entree.received_by || entree.created_by_name || '-' }}</span></div>
              <div class="admin-kv"><span class="k">Montant</span><span class="v text-success">{{ formatMoney(entree.amount) }}</span></div>
              <div class="admin-kv">
                <span class="k">Statut</span>
                <span class="v">
                  <span :class="['badge', entree.status === 'paid' ? 'badge-success' : 'badge-warning']">{{ translateStatus(entree.status) }}</span>
                </span>
              </div>
            </div>
          </div>
        </template>
        <div v-if="!loadingEntrees && filteredEntrees.length === 0" class="empty-cell">Aucune entree</div>
      </div>

      <table v-else class="admin-table">
        <thead>
          <tr>
            <th><button class="table-sort-btn" :class="{ active: isEntreeSortActive('code') }" @click="toggleEntreeSort('code')">Code <i :class="entreeSortIconClass('code')"></i></button></th>
            <th><button class="table-sort-btn" :class="{ active: isEntreeSortActive('date') }" @click="toggleEntreeSort('date')">Date <i :class="entreeSortIconClass('date')"></i></button></th>
            <th><button class="table-sort-btn" :class="{ active: isEntreeSortActive('reference') }" @click="toggleEntreeSort('reference')">Reference <i :class="entreeSortIconClass('reference')"></i></button></th>
            <th><button class="table-sort-btn" :class="{ active: isEntreeSortActive('title') }" @click="toggleEntreeSort('title')">Intitule <i :class="entreeSortIconClass('title')"></i></button></th>
            <th><button class="table-sort-btn" :class="{ active: isEntreeSortActive('received_from') }" @click="toggleEntreeSort('received_from')">Recu de <i :class="entreeSortIconClass('received_from')"></i></button></th>
            <th><button class="table-sort-btn" :class="{ active: isEntreeSortActive('received_by') }" @click="toggleEntreeSort('received_by')">Recu par <i :class="entreeSortIconClass('received_by')"></i></button></th>
            <th><button class="table-sort-btn" :class="{ active: isEntreeSortActive('amount') }" @click="toggleEntreeSort('amount')">Montant <i :class="entreeSortIconClass('amount')"></i></button></th>
            <th><button class="table-sort-btn" :class="{ active: isEntreeSortActive('status') }" @click="toggleEntreeSort('status')">Statut <i :class="entreeSortIconClass('status')"></i></button></th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <template v-if="loadingEntrees">
            <tr v-for="n in 6" :key="`entree-row-sk-${n}`">
              <td><div class="skeleton-line skeleton-w-40"></div></td>
              <td><div class="skeleton-line skeleton-w-40"></div></td>
              <td><div class="skeleton-line skeleton-w-50"></div></td>
              <td><div class="skeleton-line skeleton-w-80"></div></td>
              <td><div class="skeleton-line skeleton-w-50"></div></td>
              <td><div class="skeleton-line skeleton-w-50"></div></td>
              <td><div class="skeleton-line skeleton-w-35"></div></td>
              <td><div class="skeleton-line skeleton-w-30"></div></td>
              <td><div class="skeleton-line skeleton-w-60"></div></td>
            </tr>
          </template>
          <template v-else>
            <tr v-for="entree in paginatedEntrees" :key="entree.id">
              <td><code>{{ getEntreeDisplayId(entree) }}</code></td>
              <td>{{ entree.date }}</td>
              <td>{{ entree.reference }}</td>
              <td>
                <div class="cell-main">{{ entree.title }}</div>
                <div v-if="entree.category" class="cell-sub">{{ entree.category }}</div>
              </td>
              <td>{{ entree.received_from || '-' }}</td>
              <td>{{ entree.received_by || entree.created_by_name || '-' }}</td>
              <td class="text-success"><strong>{{ formatMoney(entree.amount) }}</strong></td>
              <td>
                <span :class="['badge', entree.status === 'paid' ? 'badge-success' : 'badge-warning']">
                  {{ translateStatus(entree.status) }}
                </span>
              </td>
              <td class="actions-cell">
                <div class="actions-dropdown">
                  <button class="btn-icon details" title="Actions" @click.stop="toggleActions(entree.id)">
                    <i class="fas fa-ellipsis-vertical"></i>
                  </button>
                  <div v-if="openActionsId === entree.id" class="actions-menu" @click.stop>
                    <button class="actions-item" @click="viewEntree(entree)">
                      <i class="fas fa-eye"></i> Voir
                    </button>
                    <button class="actions-item" @click="editEntree(entree)">
                      <i class="fas fa-edit"></i> Modifier
                    </button>
                    <button class="actions-item danger" @click="confirmDelete(entree)">
                      <i class="fas fa-trash-alt"></i> Supprimer
                    </button>
                  </div>
                </div>
              </td>
            </tr>
            <tr v-if="filteredEntrees.length === 0">
              <td colspan="9" class="empty-cell">Aucune entree</td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>

    <AdminAppModal v-model="showFormModal" :title="isEditing ? 'Modifier l entree' : 'Nouvelle entree'" width="560px">
      <form @submit.prevent="saveEntree" class="admin-form">
        <div class="form-grid">
          <div class="form-group">
            <label class="form-label">Date</label>
            <input v-model="form.date" type="date" class="form-input" required />
          </div>
          <div class="form-group">
            <label class="form-label">Reference</label>
            <input v-model="form.reference" type="text" class="form-input" required placeholder="Ex: ENT-2401" />
          </div>
        </div>
        <div class="form-group">
          <label class="form-label">Intitule</label>
          <input v-model="form.title" type="text" class="form-input" required placeholder="Ex: Vente complementaire, location, apport de caisse..." />
        </div>
        <div class="form-grid">
          <div class="form-group">
            <label class="form-label">Categorie</label>
            <input v-model="form.category" type="text" class="form-input" placeholder="Ex: Vente, Service, Divers" />
          </div>
          <div class="form-group">
            <label class="form-label">Montant (Fbu)</label>
            <input v-model="amountInput" inputmode="numeric" type="text" class="form-input" required placeholder="0" />
          </div>
        </div>
        <div class="form-grid">
          <div class="form-group">
            <label class="form-label">Recu de</label>
            <input v-model="form.received_from" type="text" class="form-input" placeholder="Client, partenaire, autre source..." />
          </div>
          <div class="form-group">
            <label class="form-label">Recu par</label>
            <input v-model="form.received_by" type="text" class="form-input" readonly />
          </div>
        </div>
        <div class="form-group">
          <label class="form-label">Statut</label>
          <select v-model="form.status" class="form-select" required>
            <option value="paid">Validee</option>
            <option value="pending">En attente</option>
          </select>
        </div>
        <div class="form-group">
          <label class="form-label">Note</label>
          <textarea v-model="form.notes" rows="3" class="form-textarea" placeholder="Commentaire ou justification..."></textarea>
        </div>
      </form>
      <template #footer>
        <button class="btn btn-outline" @click="showFormModal = false">Annuler</button>
        <button class="btn btn-primary" :class="{ 'is-loading': savingEntree }" :disabled="savingEntree" @click="saveEntree">
          {{ isEditing ? 'Mettre a jour' : 'Enregistrer' }}
        </button>
      </template>
    </AdminAppModal>

    <AdminAppModal v-model="showViewModal" title="Details de l entree" width="600px">
      <div v-if="selectedEntree" class="entity-view-modal">
        <div class="entity-view-hero">
          <div class="entity-view-avatar">{{ String(getEntreeDisplayId(selectedEntree) || 'EN').slice(0, 2).toUpperCase() }}</div>
          <div class="entity-view-main">
            <div class="entity-view-code">{{ getEntreeDisplayId(selectedEntree) }}</div>
            <h3>{{ selectedEntree.title }}</h3>
            <p>{{ selectedEntree.reference }}</p>
          </div>
          <div class="entity-view-badges">
            <span :class="['badge', selectedEntree.status === 'paid' ? 'badge-success' : 'badge-warning']">{{ translateStatus(selectedEntree.status) }}</span>
            <span class="badge badge-info">{{ formatMoney(selectedEntree.amount) }}</span>
          </div>
        </div>

        <div class="entity-view-grid">
          <section class="entity-view-card">
            <div class="entity-view-card-title">Entree</div>
            <div class="entity-view-list">
              <div class="entity-view-item"><span class="entity-view-label">Date</span><span class="entity-view-value">{{ selectedEntree.date }}</span></div>
              <div class="entity-view-item"><span class="entity-view-label">Categorie</span><span class="entity-view-value">{{ selectedEntree.category || '-' }}</span></div>
              <div class="entity-view-item"><span class="entity-view-label">Recu de</span><span class="entity-view-value">{{ selectedEntree.received_from || '-' }}</span></div>
              <div class="entity-view-item"><span class="entity-view-label">Recu par</span><span class="entity-view-value">{{ selectedEntree.received_by || selectedEntree.created_by_name || '-' }}</span></div>
              <div class="entity-view-item"><span class="entity-view-label">Note</span><span class="entity-view-value">{{ selectedEntree.notes || '-' }}</span></div>
            </div>
          </section>
          <section class="entity-view-card">
            <div class="entity-view-card-title">Suivi administratif</div>
            <div class="entity-view-list">
              <div class="entity-view-item"><span class="entity-view-label">Reference</span><span class="entity-view-value">{{ selectedEntree.reference }}</span></div>
              <div class="entity-view-item"><span class="entity-view-label">Statut</span><span class="entity-view-value">{{ translateStatus(selectedEntree.status) }}</span></div>
              <div class="entity-view-item"><span class="entity-view-label">Cree le</span><span class="entity-view-value">{{ formatDisplayDate(selectedEntree.created_at) }}</span></div>
              <div class="entity-view-item"><span class="entity-view-label">Cree par</span><span class="entity-view-value">{{ selectedEntree.created_by_name || '-' }}</span></div>
              <div class="entity-view-item"><span class="entity-view-label">Derniere action</span><span class="entity-view-value">{{ selectedEntree.updated_by_name || selectedEntree.created_by_name || '-' }}</span></div>
            </div>
          </section>
        </div>
      </div>
      <template #footer>
        <button class="btn btn-primary" @click="showViewModal = false">Fermer</button>
      </template>
    </AdminAppModal>

    <AdminAppModal v-model="showDeleteModal" title="Confirmer la suppression" width="400px">
      <p>Etes-vous sur de vouloir supprimer cette entree : <strong>{{ selectedEntree?.title }}</strong> ?</p>
      <template #footer>
        <button class="btn btn-outline" @click="showDeleteModal = false">Annuler</button>
        <button class="btn btn-danger" :class="{ 'is-loading': deletingEntree }" :disabled="deletingEntree" @click="deleteEntree">
          Supprimer
        </button>
      </template>
    </AdminAppModal>
  </div>
</template>

<script setup>
import { api } from '~/composables/useApi'
import { useMoney } from '~/composables/useMoney'
import { usePagination } from '~/composables/usePagination'
import { useDateFormat } from '~/composables/useDateFormat'
import { useTableSort } from '~/composables/useTableSort'
import { useAdminExportDocuments } from '~/composables/useAdminExportDocuments'
import { canExportAdminExcel, getStoredUser } from '~/composables/useRoleAccess'

definePageMeta({ layout: 'admin' })

const { formatMoney, moneyInputModel } = useMoney()
const { formatDisplayDate } = useDateFormat()
const { getSanitizedExportHtml, buildPdfDocumentHtml, downloadHtmlAsXls, downloadPdfHtml, buildExportFileName } = useAdminExportDocuments()

const entrees = ref([])
const currentUser = ref({})
const exportRef = ref(null)
const exportingPdf = ref(false)
const exportingXls = ref(false)
const search = ref('')
const categoryFilter = ref('')
const statusFilter = ref('')
const preset = ref('28d')
const customStart = ref('')
const customEnd = ref('')
const loadingEntrees = ref(false)
const isMobile = ref(false)
const filtersOpen = ref(false)
const openActionsId = ref(null)
const showFormModal = ref(false)
const showViewModal = ref(false)
const showDeleteModal = ref(false)
const isEditing = ref(false)
const selectedEntree = ref(null)
const savingEntree = ref(false)
const deletingEntree = ref(false)

const canExportExcel = computed(() => canExportAdminExcel(currentUser.value))

const form = ref({
  id: null,
  date: '',
  reference: '',
  title: '',
  category: 'Autre',
  amount: 0,
  received_from: '',
  received_by: '',
  notes: '',
  status: 'paid',
})

const amountInput = moneyInputModel(form, 'amount')

const toNumber = (value) => Number(value || 0)
const currentEntreeUserLabel = computed(() => (
  String(
    currentUser.value?.username ||
    currentUser.value?.full_name ||
    currentUser.value?.name ||
    currentUser.value?.email ||
    'Utilisateur connecte'
  ).trim() || 'Utilisateur connecte'
))

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
  if (value === 'all') return { start: '', end: '' }
  if (value === '7d') return { start: addDays(todayYmd, -6), end: todayYmd }
  if (value === '28d') return { start: addDays(todayYmd, -27), end: todayYmd }
  if (value === '90d') return { start: addDays(todayYmd, -89), end: todayYmd }
  if (value === 'year') return { start: `${new Date().getFullYear()}-01-01`, end: todayYmd }
  if (value === 'this_month') {
    const now = new Date()
    return { start: `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-01`, end: todayYmd }
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

const inRangeYmd = (ymd, start, end) => {
  const value = String(ymd || '').slice(0, 10)
  if (!start || !end) return true
  if (!value) return false
  return value >= start && value <= end
}

const getEntreeDisplayId = (entree) => entree?.code || 'LBE00000001'
const categories = computed(() => Array.from(new Set((entrees.value || []).map(entree => String(entree?.category || '').trim()).filter(Boolean))).sort())

const toggleActions = (id) => {
  openActionsId.value = openActionsId.value === id ? null : id
}

const closeActions = () => {
  openActionsId.value = null
}

const filteredEntrees = computed(() => {
  const q = search.value.toLowerCase().trim()
  return (entrees.value || []).filter((entree) => {
    const matchesSearch = q === '' || [
      entree.reference,
      entree.title,
      entree.category,
      entree.received_from,
      entree.received_by,
      entree.created_by_name,
      entree.code,
    ].join(' ').toLowerCase().includes(q)
    const matchesCategory = categoryFilter.value === '' || String(entree?.category || '') === categoryFilter.value
    const matchesStatus = statusFilter.value === '' || String(entree?.status || '') === statusFilter.value
    const matchesDate = inRangeYmd(entree.date || entree.created_at, rangeStartYmd.value, rangeEndYmd.value)
    return matchesSearch && matchesCategory && matchesStatus && matchesDate
  })
})

const {
  sortedItems: sortedEntrees,
  toggleSort: toggleEntreeSort,
  isSortActive: isEntreeSortActive,
  sortIconClass: entreeSortIconClass,
} = useTableSort(filteredEntrees, {
  initialKey: 'id',
  initialDirection: 'desc',
  accessors: {
    amount: entree => toNumber(entree?.amount),
  },
})

const {
  paginatedItems: paginatedEntrees,
  totalItems: entreesTotalItems,
  startIndex: entreesStartIndex,
  endIndex: entreesEndIndex,
  canPrev: entreesCanPrev,
  canNext: entreesCanNext,
  prevPage: entreesPrevPage,
  nextPage: entreesNextPage,
} = usePagination(sortedEntrees, 25)

const totalPaidEntrees = computed(() => (entrees.value || []).filter(entree => entree.status === 'paid').reduce((sum, entree) => sum + toNumber(entree.amount), 0))
const totalPendingEntrees = computed(() => (entrees.value || []).filter(entree => entree.status === 'pending').reduce((sum, entree) => sum + toNumber(entree.amount), 0))
const totalMonthlyPaid = computed(() => {
  const startOfMonth = `${new Date().getFullYear()}-${String(new Date().getMonth() + 1).padStart(2, '0')}-01`
  return (entrees.value || [])
    .filter(entree => entree.status === 'paid' && String(entree.date || '').slice(0, 10) >= startOfMonth)
    .reduce((sum, entree) => sum + toNumber(entree.amount), 0)
})

const resetForm = () => {
  form.value = {
    id: null,
    date: new Date().toISOString().split('T')[0],
    reference: `ENT-${Math.floor(1000 + Math.random() * 9000)}`,
    title: '',
    category: 'Autre',
    amount: 0,
    received_from: '',
    received_by: currentEntreeUserLabel.value,
    notes: '',
    status: 'paid',
  }
}

const resetFilters = () => {
  search.value = ''
  categoryFilter.value = ''
  statusFilter.value = ''
  preset.value = '28d'
  customStart.value = ''
  customEnd.value = ''
}

const fetchEntrees = async () => {
  loadingEntrees.value = true
  try {
    const { data } = await api.get('entrees/')
    entrees.value = Array.isArray(data) ? data : []
  } catch {
    notify('Erreur lors du chargement des entrees', 'danger')
  } finally {
    loadingEntrees.value = false
  }
}

const openAddModal = () => {
  closeActions()
  isEditing.value = false
  resetForm()
  showFormModal.value = true
}

const viewEntree = (entree) => {
  closeActions()
  selectedEntree.value = entree
  showViewModal.value = true
}

const editEntree = (entree) => {
  closeActions()
  isEditing.value = true
  form.value = {
    ...entree,
    received_by: currentEntreeUserLabel.value,
  }
  showFormModal.value = true
}

const confirmDelete = (entree) => {
  closeActions()
  selectedEntree.value = entree
  showDeleteModal.value = true
}

const translateStatus = (status) => ({
  paid: 'Validee',
  pending: 'En attente',
}[String(status || '')] || String(status || '-'))

const saveEntree = async () => {
  if (savingEntree.value) return
  savingEntree.value = true
  form.value.received_by = currentEntreeUserLabel.value
  try {
    const payload = {
      ...form.value,
      amount: toNumber(form.value.amount),
    }
    if (isEditing.value && form.value.id) {
      await api.put(`entrees/${form.value.id}/`, payload)
      notify('Entree mise a jour avec succes', 'success')
    } else {
      await api.post('entrees/', payload)
      notify('Entree enregistree avec succes', 'success')
    }
    showFormModal.value = false
    await fetchEntrees()
  } catch (error) {
    const data = error?.response?.data || {}
    notify(data.reference || data.title || data.amount || data.detail || "Impossible d'enregistrer l'entree", 'danger')
  } finally {
    savingEntree.value = false
  }
}

const deleteEntree = async () => {
  if (!selectedEntree.value?.id || deletingEntree.value) return
  deletingEntree.value = true
  try {
    await api.delete(`entrees/${selectedEntree.value.id}/`)
    notify('Entree supprimee avec succes', 'success')
    showDeleteModal.value = false
    showViewModal.value = false
    await fetchEntrees()
  } catch {
    notify("Impossible de supprimer l'entree", 'danger')
  } finally {
    deletingEntree.value = false
  }
}

const exportXls = async () => {
  if (!canExportExcel.value || !exportRef.value) return
  exportingXls.value = true
  await nextTick()
  const contentHtml = getSanitizedExportHtml(exportRef.value, { htmlMode: 'inner', removeActionsColumn: true })
  downloadHtmlAsXls({ type: 'entrees', contentHtml })
  setTimeout(() => {
    exportingXls.value = false
  }, 350)
}

const exportPdf = async () => {
  if (!exportRef.value) return
  exportingPdf.value = true
  await nextTick()
  const contentHtml = getSanitizedExportHtml(exportRef.value, { htmlMode: 'inner', removeActionsColumn: true })
  const html = buildPdfDocumentHtml({
    title: 'Entrees',
    documentTitle: buildExportFileName('entrees', 'pdf').replace(/\.pdf$/, ''),
    subtitle: 'Liste des entrees enregistrees exportee depuis l administration.',
    typeLabel: 'Entrees PDF',
    tableTitles: ['Journal des entrees'],
    periodLabel: rangeStartYmd.value && rangeEndYmd.value ? `${rangeStartYmd.value} -> ${rangeEndYmd.value}` : 'Toutes les dates',
    contentHtml,
  })
  const ok = await downloadPdfHtml({ html, fileName: buildExportFileName('entrees', 'pdf') })
  if (!ok) {
    exportingPdf.value = false
    return
  }
  setTimeout(() => {
    exportingPdf.value = false
  }, 350)
}

onMounted(() => {
  currentUser.value = getStoredUser()
  fetchEntrees()
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
    document.addEventListener('click', closeActions)
    onBeforeUnmount(() => document.removeEventListener('click', closeActions))
  }
})
</script>

<style scoped>
.admin-entrees {
  padding: 0;
}

.page-header,
.table-topbar,
.controls-top,
.header-actions {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}

.page-header {
  margin-bottom: var(--space-8);
}

.page-header h1,
.table-topbar h2 {
  margin: 0 0 0.35rem;
}

.page-header p,
.table-topbar p {
  margin: 0;
  color: var(--gray-500);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
}

.stat-card {
  display: flex;
  gap: 14px;
  align-items: flex-start;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 16px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.stat-icon.success { background: var(--success-bg); color: var(--success); }
.stat-icon.info { background: var(--info-bg); color: var(--info); }
.stat-icon.warning { background: var(--warning-bg); color: var(--warning); }
.stat-icon.primary { background: rgba(37, 99, 235, 0.12); color: #2563eb; }

.stat-label {
  display: block;
  color: var(--gray-500);
  font-size: 0.8rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.stat-value {
  display: block;
  color: var(--gray-900);
  font-size: 1.3rem;
  font-weight: 900;
  margin-top: 4px;
}

.controls {
  margin-bottom: var(--space-6);
}

.search-wrapper {
  position: relative;
  flex: 1;
  min-width: 260px;
}

.search-icon {
  position: absolute;
  top: 50%;
  left: 14px;
  transform: translateY(-50%);
  color: var(--gray-400);
}

.search-input-clean,
.filter-select-clean,
.filter-input-clean {
  width: 100%;
  min-height: 46px;
  border-radius: 14px;
  border: 1px solid var(--gray-200);
  background: var(--white);
  color: var(--gray-900);
}

.search-input-clean {
  padding: 0 14px 0 42px;
}

.filter-select-clean,
.filter-input-clean {
  padding: 0 14px;
}

.filters-toggle {
  width: 42px;
  height: 42px;
  border: 1px solid var(--gray-200);
  border-radius: 12px;
  background: var(--white);
}

.filters-panel {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
  margin-top: 14px;
}

.table-container {
  overflow: hidden;
}

.cell-main {
  font-weight: 700;
  color: var(--gray-900);
}

.cell-sub {
  color: var(--gray-500);
  font-size: 0.82rem;
  margin-top: 4px;
}

.text-success {
  color: var(--success);
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
}

.actions-item.danger {
  color: #dc2626;
}

.actions-item.danger:hover {
  background: #fef2f2;
}

.entity-view-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
  margin-top: 16px;
}

.entity-view-card {
  border: 1px solid var(--gray-200);
  border-radius: 18px;
  padding: 16px;
  background: var(--gray-50);
}

.entity-view-card-title {
  font-weight: 800;
  margin-bottom: 12px;
}

.entity-view-list {
  display: grid;
  gap: 10px;
}

.entity-view-item {
  display: flex;
  justify-content: space-between;
  gap: 10px;
}

.entity-view-label {
  color: var(--gray-500);
}

.entity-view-value {
  text-align: right;
  font-weight: 700;
}

:global(html[data-admin-theme="dark"]) .page-header p,
:global(html[data-admin-theme="dark"]) .table-topbar p,
:global(html[data-admin-theme="dark"]) .stat-label,
:global(html[data-admin-theme="dark"]) .cell-sub,
:global(html[data-admin-theme="dark"]) .entity-view-label {
  color: #cbd5e1;
}

:global(html[data-admin-theme="dark"]) .stat-value,
:global(html[data-admin-theme="dark"]) .cell-main,
:global(html[data-admin-theme="dark"]) .entity-view-value {
  color: #f8fafc;
}

:global(html[data-admin-theme="dark"]) .search-input-clean,
:global(html[data-admin-theme="dark"]) .filter-select-clean,
:global(html[data-admin-theme="dark"]) .filter-input-clean,
:global(html[data-admin-theme="dark"]) .filters-toggle,
:global(html[data-admin-theme="dark"]) .entity-view-card,
:global(html[data-admin-theme="dark"]) .actions-menu {
  background: rgba(15, 23, 42, 0.82);
  border-color: rgba(51, 65, 85, 0.95);
}

:global(html[data-admin-theme="dark"]) .actions-item {
  color: #e2e8f0;
}

:global(html[data-admin-theme="dark"]) .actions-item:hover {
  background: rgba(30, 41, 59, 0.9);
}

:global(html[data-admin-theme="dark"]) .actions-item.danger {
  color: #fca5a5;
}

:global(html[data-admin-theme="dark"]) .actions-item.danger:hover {
  background: rgba(127, 29, 29, 0.22);
}

@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 992px) {
  .filters-panel,
  .entity-view-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .stats-grid,
  .filters-panel {
    grid-template-columns: 1fr;
  }
}
</style>
