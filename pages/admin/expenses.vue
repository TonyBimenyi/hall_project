<template>
  <div class="admin-expenses">
    <div class="header-actions">
      <h1>Suivi des Dépenses Internes</h1>
      <div class="header-buttons">
        <button class="btn btn-export btn-sm" @click="exportPdf">
          <i class="fas fa-file-pdf"></i> Export PDF
        </button>
        <button class="btn btn-export btn-sm" @click="exportXls">
          <i class="fas fa-file-excel"></i> Export XLS
        </button>
        <button class="btn btn-primary" @click="openAddModal">
          <i class="fas fa-plus"></i> Enregistrer une dépense
        </button>
      </div>
    </div>

    <div class="stats-grid mb-8">
      <div class="stat-card card">
        <div class="stat-icon danger"><i class="fas fa-money-bill-wave"></i></div>
        <div class="stat-info">
          <span class="stat-label">Total ce mois</span>
          <span class="stat-value">{{ totalMonthlyExpenses.toLocaleString() }} Fbu</span>
        </div>
      </div>
      <div class="stat-card card">
        <div class="stat-icon info"><i class="fas fa-tools"></i></div>
        <div class="stat-info">
          <span class="stat-label">Maintenance</span>
          <span class="stat-value">{{ maintenanceTotal.toLocaleString() }} Fbu</span>
        </div>
      </div>
      <div class="stat-card card">
        <div class="stat-icon primary"><i class="fas fa-shopping-cart"></i></div>
        <div class="stat-info">
          <span class="stat-label">Achats Matériel</span>
          <span class="stat-value">{{ equipmentTotal.toLocaleString() }} Fbu</span>
        </div>
      </div>
      <div class="stat-card card">
        <div class="stat-icon success"><i class="fas fa-user-tie"></i></div>
        <div class="stat-info">
          <span class="stat-label">Salaires</span>
          <span class="stat-value">{{ salariesTotal.toLocaleString() }} Fbu</span>
        </div>
      </div>
    </div>

    <div class="controls card">
      <div class="search-wrapper">
        <i class="fas fa-search search-icon"></i>
        <input
          type="text"
          v-model="search"
          placeholder="Rechercher (description, bénéficiaire, payé par)..."
          class="search-input-clean"
        />
      </div>
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

    <div class="table-container card">
      <table ref="tableRef" class="admin-table">
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
          <tr v-for="expense in filteredExpenses" :key="expense.id">
            <td>{{ expense.date }}</td>
            <td><strong>{{ expense.description }}</strong></td>
            <td>{{ expense.category }}</td>
            <td>{{ expense.amount.toLocaleString() }} Fbu</td>
            <td>{{ expense.paid_by }}</td>
            <td>
              <span :class="['badge', expense.status === 'paid' ? 'badge-success' : 'badge-warning']">
                {{ translateStatus(expense.status) }}
              </span>
            </td>
            <td>
              <div class="btn-group">
                <button class="btn-icon view" title="Voir détails" @click="viewExpense(expense)">
                  <i class="fas fa-eye"></i>
                </button>
                <button class="btn-icon edit" title="Modifier" @click="editExpense(expense)">
                  <i class="fas fa-edit"></i>
                </button>
                <button class="btn-icon delete" title="Supprimer" @click="confirmDelete(expense)">
                  <i class="fas fa-trash-alt"></i>
                </button>
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
            <input v-model.number="form.amount" type="number" class="form-input" required />
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
        <button class="btn btn-primary" @click="saveExpense">{{ isEditing ? 'Mettre à jour' : 'Enregistrer' }}</button>
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
          <span class="detail-val">{{ selectedExpense.amount.toLocaleString() }} Fbu</span>
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
        <button class="btn btn-danger" @click="deleteExpense">Supprimer</button>
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

const expenses = ref([])
const tableRef = ref(null)
const search = ref('')
const categoryFilter = ref('')
const statusFilter = ref('')
const dateFrom = ref('')
const dateTo = ref('')

const exportXls = () => {
  if (!tableRef.value) return
  const html = `<!doctype html><html><head><meta charset="utf-8"></head><body>${tableRef.value.outerHTML}</body></html>`
  const blob = new Blob([html], { type: 'application/vnd.ms-excel' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'expenses.xls'
  a.click()
  URL.revokeObjectURL(url)
}

const exportPdf = () => {
  if (!tableRef.value) return
  const win = window.open('', '_blank')
  if (!win) return
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
}

const fetchExpenses = async () => {
  try {
    const response = await api.get('expenses/')
    expenses.value = response.data
  } catch (error) {
    notify('Erreur lors du chargement des dépenses', 'danger')
  }
}

onMounted(() => {
  fetchExpenses()
})

const totalMonthlyExpenses = computed(() => expenses.value.reduce((acc, exp) => acc + parseFloat(exp.amount), 0))
const maintenanceTotal = computed(() => expenses.value.filter(e => e.category === 'Maintenance').reduce((acc, exp) => acc + parseFloat(exp.amount), 0))
const equipmentTotal = computed(() => expenses.value.filter(e => e.category === 'Équipement').reduce((acc, exp) => acc + parseFloat(exp.amount), 0))
const salariesTotal = computed(() => expenses.value.filter(e => e.category === 'Salaires').reduce((acc, exp) => acc + parseFloat(exp.amount), 0))

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
  selectedExpense.value = expense
  showViewModal.value = true
}

const editExpense = (expense) => {
  isEditing.value = true
  form.value = { ...expense }
  showFormModal.value = true
}

const confirmDelete = (expense) => {
  selectedExpense.value = expense
  showDeleteModal.value = true
}

const saveExpense = async () => {
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
  }
}

const deleteExpense = async () => {
  try {
    await api.delete(`expenses/${selectedExpense.value.id}/`)
    notify('Dépense supprimée', 'danger')
    showDeleteModal.value = false
    fetchExpenses()
  } catch (error) {
    notify('Erreur lors de la suppression', 'danger')
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
  align-items: center;
  margin-bottom: var(--space-10);
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

.static-info {
  margin-top: var(--space-12);
  color: #cbd5e1;
  font-size: 0.85rem;
  text-align: center;
  font-weight: 600;
}
</style>
