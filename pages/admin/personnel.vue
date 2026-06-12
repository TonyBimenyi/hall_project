<!-- pages/admin/personnel.vue -->
<template>
  <div class="personnel-page">
    <div class="page-header">
      <div>
        <h1>Gestion du Personnel</h1>
        <p>Suivi des employés et assignation des tâches</p>
      </div>
      <div class="header-actions">
        <button class="btn btn-export btn-sm" :class="{ 'is-loading': exportingPdf }" :disabled="exportingPdf || exportingXls" @click="exportPdf">
          <i class="fas fa-file-pdf"></i> Export PDF
        </button>
        <button class="btn btn-export btn-sm" :class="{ 'is-loading': exportingXls }" :disabled="exportingPdf || exportingXls" @click="exportXls">
          <i class="fas fa-file-excel"></i> Export XLS
        </button>
        <button v-if="canManagePersonnelAccounts" class="btn btn-primary btn-sm" @click="openAddModal">
          <i class="fas fa-user-plus"></i> Ajouter un employé
        </button>
      </div>
    </div>

    <div class="stats-grid mb-8">
      <div class="stat-card card">
        <div class="stat-icon primary"><i class="fas fa-users"></i></div>
        <div class="stat-info">
          <span class="label">Total Personnel</span>
          <span class="value">
            <span v-if="loadingPersonnel" class="skeleton-line skeleton-w-30"></span>
            <template v-else>{{ displayPersonnelCount }}</template>
          </span>
        </div>
      </div>
      <div class="stat-card card">
        <div class="stat-icon success"><i class="fas fa-user-check"></i></div>
        <div class="stat-info">
          <span class="label">En service</span>
          <span class="value success">
            <span v-if="loadingPersonnel" class="skeleton-line skeleton-w-30"></span>
            <template v-else>{{ displayOnDutyCount }}</template>
          </span>
        </div>
      </div>
      <div class="stat-card card">
        <div class="stat-icon info"><i class="fas fa-tasks"></i></div>
        <div class="stat-info">
          <span class="label">Disponibles</span>
          <span class="value info">
            <span v-if="loadingPersonnel" class="skeleton-line skeleton-w-30"></span>
            <template v-else>{{ displayAvailableCount }}</template>
          </span>
        </div>
      </div>
      <div class="stat-card card">
        <div class="stat-icon warning"><i class="fas fa-user-clock"></i></div>
        <div class="stat-info">
          <span class="label">En congé</span>
          <span class="value warning">
            <span v-if="loadingPersonnel" class="skeleton-line skeleton-w-30"></span>
            <template v-else>{{ displayOffDutyCount }}</template>
          </span>
        </div>
      </div>
    </div>

    <div class="table-container card">
      <div style="display:flex; align-items:center; justify-content:flex-end; gap:12px; flex-wrap:wrap; margin-bottom: var(--space-4);">
        <AdminAppTablePagination
          :start="personnelStartIndex"
          :end="personnelEndIndex"
          :total="personnelTotalItems"
          :can-prev="personnelCanPrev"
          :can-next="personnelCanNext"
          :disabled="loadingPersonnel"
          @prev="personnelPrevPage"
          @next="personnelNextPage"
        />
      </div>
      <div v-if="isMobile" class="admin-cards">
        <template v-if="loadingPersonnel">
          <div v-for="n in 6" :key="`sk-card-${n}`" class="admin-card">
            <div class="admin-card-head">
              <div style="width: 100%;">
                <div class="skeleton-line skeleton-w-60"></div>
                <div style="margin-top: 8px;" class="skeleton-line skeleton-w-40"></div>
              </div>
            </div>
            <div class="admin-card-body">
              <div class="skeleton-line skeleton-w-50"></div>
              <div class="skeleton-line skeleton-w-40"></div>
              <div class="skeleton-line skeleton-w-30"></div>
            </div>
          </div>
        </template>
        <template v-else>
          <div v-for="staff in paginatedPersonnel" :key="staff.id" class="admin-card">
            <div class="admin-card-head">
              <div>
                <div class="admin-card-title">{{ staff.name }}</div>
                <div class="admin-card-subtitle">{{ getStaffDisplayId(staff) }} • {{ staff.role }} • {{ staff.account_username || staff.phone || '-' }}</div>
              </div>

              <div class="actions-dropdown">
                <button class="btn-icon details" title="Détails" @click.stop="toggleActions(staff.id)">
                  <i class="fas fa-ellipsis-vertical"></i>
                </button>
                <div v-if="openActionsId === staff.id" class="actions-menu" @click.stop>
                  <button class="actions-item" @click="viewStaff(staff)">
                    <i class="fas fa-eye"></i> Voir
                  </button>
                  <button v-if="canManagePersonnelAccounts" class="actions-item" @click="editStaff(staff)">
                    <i class="fas fa-edit"></i> Modifier
                  </button>
                  <button v-if="canManagePersonnelAccounts" class="actions-item danger" @click="confirmDelete(staff)">
                    <i class="fas fa-trash-alt"></i> Supprimer
                  </button>
                </div>
              </div>
            </div>

            <div class="admin-card-body">
              <div class="admin-kv">
                <span class="k">ID</span>
                <span class="v">{{ getStaffDisplayId(staff) }}</span>
              </div>
              <div class="admin-kv">
                <span class="k">Statut</span>
                <span class="v">
                  <span :class="['badge', getBadgeClass(staff.status)]">{{ translateStatus(staff.status) }}</span>
                </span>
              </div>
              <div class="admin-kv">
                <span class="k">Compte</span>
                <span class="v">{{ accountStatusText(staff) }}</span>
              </div>
            </div>
          </div>
        </template>
        <div v-if="!loadingPersonnel && personnel.length === 0" class="empty-cell">Aucun employé</div>
      </div>

      <table v-else ref="tableRef" class="admin-table">
        <thead>
          <tr>
            <th><button class="table-sort-btn" :class="{ active: isPersonnelSortActive('id') }" @click="togglePersonnelSort('id')">ID <i :class="personnelSortIconClass('id')"></i></button></th>
            <th><button class="table-sort-btn" :class="{ active: isPersonnelSortActive('name') }" @click="togglePersonnelSort('name')">Employé <i :class="personnelSortIconClass('name')"></i></button></th>
            <th><button class="table-sort-btn" :class="{ active: isPersonnelSortActive('role') }" @click="togglePersonnelSort('role')">Rôle <i :class="personnelSortIconClass('role')"></i></button></th>
            <th><button class="table-sort-btn" :class="{ active: isPersonnelSortActive('phone') }" @click="togglePersonnelSort('phone')">Contact <i :class="personnelSortIconClass('phone')"></i></button></th>
            <th><button class="table-sort-btn" :class="{ active: isPersonnelSortActive('has_account') }" @click="togglePersonnelSort('has_account')">Compte <i :class="personnelSortIconClass('has_account')"></i></button></th>
            <th><button class="table-sort-btn" :class="{ active: isPersonnelSortActive('status') }" @click="togglePersonnelSort('status')">Disponibilité <i :class="personnelSortIconClass('status')"></i></button></th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <template v-if="loadingPersonnel">
            <tr v-for="n in 6" :key="`sk-${n}`">
              <td><div class="skeleton-line skeleton-w-50"></div></td>
              <td class="staff-cell">
                <div class="skeleton-lines">
                  <div class="skeleton-line skeleton-w-60"></div>
                  <div class="skeleton-line skeleton-w-40"></div>
                </div>
              </td>
              <td><div class="skeleton-line skeleton-w-50"></div></td>
              <td><div class="skeleton-line skeleton-w-50"></div></td>
              <td><div class="skeleton-line skeleton-w-40"></div></td>
              <td><div class="skeleton-line skeleton-w-30"></div></td>
              <td><div class="skeleton-line skeleton-w-60"></div></td>
            </tr>
          </template>
          <tr v-else v-for="staff in paginatedPersonnel" :key="staff.id">
            <td><code>{{ getStaffDisplayId(staff) }}</code></td>
            <td class="staff-cell">
              <div class="avatar">{{ staff.name.charAt(0) }}</div>
              <div class="staff-info">
                <div class="name">{{ staff.name }}</div>
                <div class="id">{{ staff.role }}</div>
              </div>
            </td>
            <td>{{ staff.role }}</td>
            <td>
              <div>{{ staff.account_username || '-' }}</div>
              <div v-if="staff.phone" class="muted-line">{{ staff.phone }}</div>
              <div v-if="staff.email" class="muted-line">{{ staff.email }}</div>
            </td>
            <td>
              <span class="badge" :class="staff.has_account ? (staff.must_change_password ? 'badge-warning' : 'badge-success') : 'badge-info'">
                {{ accountStatusText(staff) }}
              </span>
            </td>
            <td>
              <span :class="['badge', getBadgeClass(staff.status)]">
                {{ translateStatus(staff.status) }}
              </span>
            </td>
            <td class="actions-cell">
              <div class="actions-dropdown">
                <button class="btn-icon details" title="Détails" @click.stop="toggleActions(staff.id)">
                  <i class="fas fa-ellipsis-vertical"></i>
                </button>
                <div v-if="openActionsId === staff.id" class="actions-menu" @click.stop>
                  <button class="actions-item" @click="viewStaff(staff)">
                    <i class="fas fa-eye"></i> Voir
                  </button>
                  <button v-if="canManagePersonnelAccounts" class="actions-item" @click="editStaff(staff)">
                    <i class="fas fa-edit"></i> Modifier
                  </button>
                  <button v-if="canManagePersonnelAccounts" class="actions-item danger" @click="confirmDelete(staff)">
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
    <AdminAppModal v-model="showFormModal" :title="isEditing ? 'Modifier l\'employé' : 'Ajouter un employé'" width="500px">
      <form @submit.prevent="saveStaff" class="admin-form">
        <div class="form-group">
          <label class="form-label">Prénom</label>
          <input v-model="form.first_name" type="text" class="form-input" required placeholder="Ex: Jean" />
        </div>
        <div class="form-group">
          <label class="form-label">Nom</label>
          <input v-model="form.last_name" type="text" class="form-input" required placeholder="Ex: Dupont" />
        </div>
        <div class="form-group">
          <label class="form-label">Rôle</label>
          <select v-model="form.role" class="form-select" required>
            <option value="Proprietaire">Proprietaire</option>
            <option value="Gestionnaire">Gestionnaire</option>
            <option value="Gerant">Gerant</option>
            <option value="Réceptionniste">Réceptionniste</option>
            <option value="Sécurité">Sécurité</option>
            <option value="Chef Cuisine">Chef Cuisine</option>
            <option value="Entretien">Entretien</option>
            <option value="Technicien AV">Technicien AV</option>
            <option value="Serveur">Serveur</option>
          </select>
        </div>
        <div v-if="(!isEditing && form.create_account) || (isEditing && form.has_account)" class="form-group">
          <label class="form-label">Nom d'utilisateur</label>
          <input v-model="form.username" type="text" class="form-input" :required="form.create_account || form.has_account" placeholder="Ex: reception-01" />
        </div>
        <div class="form-group">
          <label class="form-label">Téléphone (optionnel)</label>
          <input v-model="form.phone" type="text" class="form-input" placeholder="+257 ..." />
        </div>
        <div class="form-group">
          <label class="form-label">Email</label>
          <input v-model="form.email" type="email" class="form-input" placeholder="email@exemple.com" />
        </div>
        <div class="form-group">
          <label class="form-label">Statut</label>
          <select v-model="form.status" class="form-select" required>
            <option value="available">Disponible</option>
            <option value="on_duty">En service</option>
            <option value="off_duty">En congé</option>
          </select>
        </div>
        <div v-if="!isEditing && canManagePersonnelAccounts" class="form-group inline-check">
          <label class="checkbox-row">
            <input v-model="form.create_account" type="checkbox" />
            <span>Créer un accès au tableau de bord avec mot de passe temporaire</span>
          </label>
        </div>
        <div v-if="!isEditing && form.create_account" class="form-group">
          <label class="form-label">Mot de passe temporaire</label>
          <input v-model="form.temporary_password" type="text" class="form-input" :required="form.create_account" minlength="8" placeholder="Ex: Temp@2026" />
          <small class="helper-text">L'employé devra changer ce mot de passe à sa première connexion.</small>
        </div>
        <div v-if="isEditing && form.has_account" class="account-note">
          <i class="fas fa-key"></i>
          <span>Ce personnel a déjà un compte de connexion.</span>
        </div>
      </form>
      <template #footer>
        <button class="btn btn-outline" @click="showFormModal = false">Annuler</button>
        <button class="btn btn-primary" :class="{ 'is-loading': savingStaff }" :disabled="savingStaff || !canManagePersonnelAccounts" @click="saveStaff">
          {{ isEditing ? 'Mettre à jour' : 'Ajouter' }}
        </button>
      </template>
    </AdminAppModal>

    <!-- View Modal -->
    <AdminAppModal v-model="showViewModal" title="Détails de l'employé" width="400px">
      <div v-if="selectedStaff" class="view-details">
        <div class="detail-item">
          <span class="detail-label">ID</span>
          <span class="detail-val">{{ getStaffDisplayId(selectedStaff) }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">Nom</span>
          <span class="detail-val">{{ selectedStaff.name }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">Rôle</span>
          <span class="detail-val">{{ selectedStaff.role }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">Contact</span>
          <span class="detail-val">{{ selectedStaff.phone || '-' }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">Email</span>
          <span class="detail-val">{{ selectedStaff.email || '-' }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">Compte</span>
          <span class="detail-val">{{ accountStatusText(selectedStaff) }}</span>
        </div>
        <div v-if="selectedStaff.account_username" class="detail-item">
          <span class="detail-label">Identifiant</span>
          <span class="detail-val">{{ selectedStaff.account_username }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">Statut</span>
          <span :class="['badge', getBadgeClass(selectedStaff.status)]">
            {{ translateStatus(selectedStaff.status) }}
          </span>
        </div>
        <div class="detail-item">
          <span class="detail-label">Créé par</span>
          <span class="detail-val">{{ selectedStaff.created_by_name || '-' }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">Dernière action par</span>
          <span class="detail-val">{{ selectedStaff.updated_by_name || selectedStaff.created_by_name || '-' }}</span>
        </div>
      </div>
      <template #footer>
        <button class="btn btn-primary" @click="showViewModal = false">Fermer</button>
      </template>
    </AdminAppModal>

    <!-- Delete Confirmation Modal -->
    <AdminAppModal v-model="showDeleteModal" title="Confirmer la suppression" width="400px">
      <p>Êtes-vous sûr de vouloir supprimer l'employé <strong>{{ selectedStaff?.name }}</strong> ? Cette action est irréversible.</p>
      <template #footer>
        <button class="btn btn-outline" @click="showDeleteModal = false">Annuler</button>
        <button class="btn btn-danger" :class="{ 'is-loading': deletingStaff }" :disabled="deletingStaff" @click="deleteStaff">
          Supprimer
        </button>
      </template>
    </AdminAppModal>
  </div>
</template>

<script setup>
import { notify } from '~/composables/useNotification'
import { api } from '~/composables/useApi'
import { usePagination } from '~/composables/usePagination'
import { useDisplayIds } from '~/composables/useDisplayIds'
import { useTableSort } from '~/composables/useTableSort'
import { canManageStaffAccounts as canManageStaffAccountsByRole } from '~/composables/useRoleAccess'

definePageMeta({ layout: 'admin' })

const personnel = ref([])
const { buildPersonnelSequenceMap } = useDisplayIds()
const {
  sortedItems: sortedPersonnel,
  toggleSort: togglePersonnelSort,
  isSortActive: isPersonnelSortActive,
  sortIconClass: personnelSortIconClass,
} = useTableSort(computed(() => personnel.value), {
  initialKey: 'id',
  initialDirection: 'desc',
  accessors: {
    has_account: staff => (staff?.has_account ? 1 : 0),
  },
})
const {
  paginatedItems: paginatedPersonnel,
  totalItems: personnelTotalItems,
  startIndex: personnelStartIndex,
  endIndex: personnelEndIndex,
  canPrev: personnelCanPrev,
  canNext: personnelCanNext,
  prevPage: personnelPrevPage,
  nextPage: personnelNextPage,
} = usePagination(sortedPersonnel, 50)
const tableRef = ref(null)
const exportingPdf = ref(false)
const exportingXls = ref(false)
const loadingPersonnel = ref(false)
const openActionsId = ref(null)
const isMobile = ref(false)
const savingStaff = ref(false)
const deletingStaff = ref(false)
const currentUser = ref({})

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
  a.download = 'personnel.xls'
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
  win.document.write(`<!doctype html><html><head><meta charset="utf-8"><title>Personnel</title><style>
  body{font-family:Arial, sans-serif; padding:20px}
  table{width:100%; border-collapse:collapse}
  th,td{border:1px solid #e2e8f0; padding:8px; text-align:left; font-size:12px}
  th{background:#f8fafc}
  </style></head><body><h2>Personnel</h2>${tableRef.value.outerHTML}</body></html>`)
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
const isEditing = ref(false)
const selectedStaff = ref(null)

const form = ref({
  id: null,
  first_name: '',
  last_name: '',
  role: 'Serveur',
  username: '',
  phone: '',
  email: '',
  status: 'available'
})

const fetchPersonnel = async () => {
  loadingPersonnel.value = true
  try {
    const response = await api.get('personnel/')
    personnel.value = Array.isArray(response.data) ? response.data : []
  } catch (error) {
    notify('Erreur lors du chargement du personnel', 'danger')
  } finally {
    loadingPersonnel.value = false
  }
}

onMounted(() => {
  try {
    currentUser.value = JSON.parse(localStorage.getItem('user') || '{}')
  } catch {
    currentUser.value = {}
  }
  fetchPersonnel()
  if (process.client) {
    const update = () => { isMobile.value = window.innerWidth <= 992 }
    update()
    window.addEventListener('resize', update)
    onBeforeUnmount(() => window.removeEventListener('resize', update))

    const onDocClick = () => { openActionsId.value = null }
    document.addEventListener('click', onDocClick)
    onBeforeUnmount(() => document.removeEventListener('click', onDocClick))
  }
})

const onDutyCount = computed(() => personnel.value.filter(p => p.status === 'on_duty').length)
const availableCount = computed(() => personnel.value.filter(p => p.status === 'available').length)
const offDutyCount = computed(() => personnel.value.filter(p => p.status === 'off_duty').length)
const staffDisplayIds = computed(() => buildPersonnelSequenceMap(personnel.value))
const getStaffDisplayId = (staff) => staffDisplayIds.value.get(staff?.id) || 'EMP-0001'
const canManagePersonnelAccounts = computed(() => !!currentUser.value?.can_manage_staff_accounts || canManageStaffAccountsByRole(currentUser.value))

const displayPersonnelCount = ref(0)
const displayOnDutyCount = ref(0)
const displayAvailableCount = ref(0)
const displayOffDutyCount = ref(0)

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

watch(() => personnel.value.length, (v) => animateCounter(displayPersonnelCount, v), { immediate: true })
watch(onDutyCount, (v) => animateCounter(displayOnDutyCount, v), { immediate: true })
watch(availableCount, (v) => animateCounter(displayAvailableCount, v), { immediate: true })
watch(offDutyCount, (v) => animateCounter(displayOffDutyCount, v), { immediate: true })

onBeforeUnmount(() => {
  for (const id of rafMap.values()) cancelAnimationFrame(id)
})

const resetForm = () => {
  form.value = {
    id: null,
    first_name: '',
    last_name: '',
    role: 'Serveur',
    email: '',
    username: '',
    phone: '',
    status: 'available',
    create_account: true,
    temporary_password: '',
    has_account: false,
  }
}

const openAddModal = () => {
  isEditing.value = false
  resetForm()
  showFormModal.value = true
}

const viewStaff = (staff) => {
  closeActions()
  selectedStaff.value = staff
  showViewModal.value = true
}

const editStaff = (staff) => {
  closeActions()
  isEditing.value = true
  const rawName = String(staff?.name || '').trim()
  const parts = rawName.split(' ').filter(Boolean)
  const first_name = parts[0] || ''
  const last_name = parts.length > 1 ? parts.slice(1).join(' ') : ''
  form.value = {
    ...staff,
    first_name,
    last_name,
    username: staff?.account_username || '',
    create_account: !!staff.has_account,
    temporary_password: '',
  }
  showFormModal.value = true
}

const confirmDelete = (staff) => {
  closeActions()
  selectedStaff.value = staff
  showDeleteModal.value = true
}

const saveStaff = async () => {
  if (savingStaff.value) return
  savingStaff.value = true
  try {
    const fullName = `${String(form.value.first_name || '').trim()} ${String(form.value.last_name || '').trim()}`.trim()
    const payload = {
      name: fullName,
      role: form.value.role,
      email: form.value.email,
      phone: form.value.phone,
      status: form.value.status,
      username: form.value.username,
    }

    if (!isEditing.value) {
      payload.create_account = !!form.value.create_account
      payload.temporary_password = form.value.temporary_password
    }

    if (isEditing.value) {
      await api.put(`personnel/${form.value.id}/`, payload)
      notify('Personnel mis à jour avec succès')
    } else {
      await api.post('personnel/', payload)
      notify('Nouvel employé ajouté avec succès')
    }
    showFormModal.value = false
    fetchPersonnel()
  } catch (error) {
    const data = error?.response?.data || {}
    const msg = data.detail || data.username || data.phone || data.email || data.temporary_password || 'Erreur lors de l\'enregistrement'
    notify(msg, 'danger')
  } finally {
    savingStaff.value = false
  }
}

const deleteStaff = async () => {
  if (deletingStaff.value || !selectedStaff.value?.id) return
  deletingStaff.value = true
  try {
    await api.delete(`personnel/${selectedStaff.value.id}/`)
    notify('Employé supprimé', 'danger')
    showDeleteModal.value = false
    fetchPersonnel()
  } catch (error) {
    notify('Erreur lors de la suppression', 'danger')
  } finally {
    deletingStaff.value = false
  }
}

const translateStatus = (status) => {
  const map = {
    available: 'Disponible',
    on_duty: 'En service',
    off_duty: 'En congé'
  }
  return map[status] || status
}

const getBadgeClass = (status) => {
  const map = {
    available: 'badge-info',
    on_duty: 'badge-success',
    off_duty: 'badge-warning'
  }
  return map[status] || ''
}

const accountStatusText = (staff) => {
  if (!staff?.has_account) return 'Sans compte'
  return staff.must_change_password ? 'Mot de passe temporaire' : 'Compte actif'
}
</script>

<style scoped>
.personnel-page {
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

.muted-line {
  color: #94a3b8;
  font-size: 0.82rem;
  margin-top: 0.15rem;
}

.inline-check {
  margin-top: 0.25rem;
}

.checkbox-row {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  font-weight: 600;
  color: #334155;
}

.checkbox-row input {
  width: 16px;
  height: 16px;
}

.helper-text {
  display: block;
  margin-top: 0.4rem;
  color: #64748b;
  font-size: 0.82rem;
}

.account-note {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.85rem 1rem;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  color: #334155;
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

.stat-icon.primary { background: #f1f5f9; color: #0f172a; }
.stat-icon.success { background: #f0fdf4; color: #22c55e; }
.stat-icon.info { background: #f0f9ff; color: #0ea5e9; }
.stat-icon.warning { background: #fffbeb; color: #f59e0b; }

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-card .label {
  font-size: 0.7rem;
  color: #94a3b8;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.125rem;
}

.stat-card .value {
  font-size: 1.5rem;
  font-weight: 800;
  color: #0f172a;
  line-height: 1.2;
}

.value.success { color: #22c55e; }
.value.info { color: #0ea5e9; }
.value.warning { color: #f59e0b; }

.staff-cell {
  display: flex;
  align-items: center;
  gap: var(--space-4);
}

.avatar {
  width: 36px;
  height: 36px;
  background: #f1f5f9;
  color: #475569;
  border-radius: var(--rounded-full);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 0.8rem;
}

.staff-info .name {
  font-weight: 700;
  color: #0f172a;
  font-size: 0.95rem;
}

.staff-info .id {
  font-size: 0.75rem;
  color: #94a3b8;
  font-weight: 500;
}

.btn-icon {
  width: 34px;
  height: 34px;
  background: #f8fafc;
  color: #94a3b8;
}

.btn-icon:hover {
  background: #f1f5f9;
}

.btn-icon.info:hover { color: var(--info); }

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
</style>
