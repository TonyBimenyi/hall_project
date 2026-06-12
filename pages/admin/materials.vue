<template>
  <div class="admin-materials">
    <div class="header-actions">
      <h1>Gestion du Matériel</h1>
      <div class="header-buttons">
        <button class="btn btn-export btn-sm" :class="{ 'is-loading': exportingPdf }" :disabled="exportingPdf || exportingXls" @click="exportPdf">
          <i class="fas fa-file-pdf"></i> Export PDF
        </button>
        <button class="btn btn-export btn-sm" :class="{ 'is-loading': exportingXls }" :disabled="exportingPdf || exportingXls" @click="exportXls">
          <i class="fas fa-file-excel"></i> Export XLS
        </button>
        <button class="btn btn-primary btn-sm" @click="openAddModal">
          <i class="fas fa-plus"></i> Ajouter du matériel
        </button>
      </div>
    </div>

    <div class="stats-grid mb-8">
      <div class="stat-card card">
        <div class="stat-icon primary"><i class="fas fa-boxes"></i></div>
        <div class="stat-info">
          <span class="stat-label">Articles</span>
          <span class="stat-value">
            <span v-if="loadingMaterials" class="skeleton-line skeleton-w-40"></span>
            <template v-else>{{ displayMaterialsCount }}</template>
          </span>
        </div>
      </div>
      <div class="stat-card card">
        <div class="stat-icon success"><i class="fas fa-check-circle"></i></div>
        <div class="stat-info">
          <span class="stat-label">En Stock</span>
          <span class="stat-value success">
            <span v-if="loadingMaterials" class="skeleton-line skeleton-w-50"></span>
            <template v-else>{{ displayTotalAvailable.toLocaleString() }}</template>
          </span>
        </div>
      </div>
      <div class="stat-card card">
        <div class="stat-icon warning"><i class="fas fa-tools"></i></div>
        <div class="stat-info">
          <span class="stat-label">Endommagé</span>
          <span class="stat-value warning">
            <span v-if="loadingMaterials" class="skeleton-line skeleton-w-50"></span>
            <template v-else>{{ displayTotalDamaged.toLocaleString() }}</template>
          </span>
        </div>
      </div>
      <div class="stat-card card">
        <div class="stat-icon danger"><i class="fas fa-times-circle"></i></div>
        <div class="stat-info">
          <span class="stat-label">Perdu</span>
          <span class="stat-value danger">
            <span v-if="loadingMaterials" class="skeleton-line skeleton-w-50"></span>
            <template v-else>{{ displayTotalLost.toLocaleString() }}</template>
          </span>
        </div>
      </div>
    </div>

    <div class="table-container card">
      <div style="display:flex; align-items:center; justify-content:flex-end; gap:12px; flex-wrap:wrap; margin-bottom: var(--space-4);">
        <AdminAppTablePagination
          :start="materialsStartIndex"
          :end="materialsEndIndex"
          :total="materialsTotalItems"
          :can-prev="materialsCanPrev"
          :can-next="materialsCanNext"
          :disabled="loadingMaterials"
          @prev="materialsPrevPage"
          @next="materialsNextPage"
        />
      </div>
      <div v-if="isMobile" class="admin-cards">
        <template v-if="loadingMaterials">
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
          <div v-for="item in paginatedMaterials" :key="item.id" class="admin-card">
            <div class="admin-card-head">
              <div>
                <div class="admin-card-title">{{ item.name }}</div>
                <div class="admin-card-subtitle">{{ getMaterialDisplayId(item) }} • {{ item.category }}</div>
              </div>

              <div class="actions-dropdown">
                <button class="btn-icon details" title="Détails" @click.stop="toggleActions(item.id)">
                  <i class="fas fa-ellipsis-vertical"></i>
                </button>
                <div v-if="openActionsId === item.id" class="actions-menu" @click.stop>
                  <button class="actions-item" @click="openQtyModal(item, 'damaged')">
                    <i class="fas fa-tools"></i> Endommagé
                  </button>
                  <button class="actions-item" @click="openQtyModal(item, 'lost')">
                    <i class="fas fa-times-circle"></i> Perdu
                  </button>
                  <button class="actions-item" @click="viewMaterial(item)">
                    <i class="fas fa-eye"></i> Voir
                  </button>
                  <button class="actions-item" @click="editMaterial(item)">
                    <i class="fas fa-edit"></i> Modifier
                  </button>
                  <button class="actions-item danger" @click="confirmDelete(item)">
                    <i class="fas fa-trash-alt"></i> Supprimer
                  </button>
                </div>
              </div>
            </div>

            <div class="admin-card-body">
              <div class="admin-kv">
                <span class="k">ID</span>
                <span class="v">{{ getMaterialDisplayId(item) }}</span>
              </div>
              <div class="admin-kv">
                <span class="k">Total</span>
                <span class="v">{{ item.total_quantity }}</span>
              </div>
              <div class="admin-kv">
                <span class="k">En stock</span>
                <span class="v">{{ item.available_quantity }}</span>
              </div>
              <div class="admin-kv">
                <span class="k">Endommagé</span>
                <span class="v">{{ (item.damaged_quantity || 0).toLocaleString() }}</span>
              </div>
              <div class="admin-kv">
                <span class="k">Perdu</span>
                <span class="v">{{ (item.lost_quantity || 0).toLocaleString() }}</span>
              </div>
            </div>
          </div>
        </template>
        <div v-if="!loadingMaterials && materials.length === 0" class="empty-cell">Aucun matériel</div>
      </div>

      <table v-else ref="tableRef" class="admin-table">
        <thead>
          <tr>
            <th><button class="table-sort-btn" :class="{ active: isMaterialSortActive('id') }" @click="toggleMaterialSort('id')">ID <i :class="materialSortIconClass('id')"></i></button></th>
            <th><button class="table-sort-btn" :class="{ active: isMaterialSortActive('name') }" @click="toggleMaterialSort('name')">Nom <i :class="materialSortIconClass('name')"></i></button></th>
            <th><button class="table-sort-btn" :class="{ active: isMaterialSortActive('category') }" @click="toggleMaterialSort('category')">Catégorie <i :class="materialSortIconClass('category')"></i></button></th>
            <th><button class="table-sort-btn" :class="{ active: isMaterialSortActive('total_quantity') }" @click="toggleMaterialSort('total_quantity')">Quantité Totale <i :class="materialSortIconClass('total_quantity')"></i></button></th>
            <th><button class="table-sort-btn" :class="{ active: isMaterialSortActive('available_quantity') }" @click="toggleMaterialSort('available_quantity')">En Stock <i :class="materialSortIconClass('available_quantity')"></i></button></th>
            <th><button class="table-sort-btn" :class="{ active: isMaterialSortActive('damaged_quantity') }" @click="toggleMaterialSort('damaged_quantity')">Endommagé <i :class="materialSortIconClass('damaged_quantity')"></i></button></th>
            <th><button class="table-sort-btn" :class="{ active: isMaterialSortActive('lost_quantity') }" @click="toggleMaterialSort('lost_quantity')">Perdu <i :class="materialSortIconClass('lost_quantity')"></i></button></th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <template v-if="loadingMaterials">
            <tr v-for="n in 6" :key="`sk-${n}`">
              <td><div class="skeleton-line skeleton-w-40"></div></td>
              <td><div class="skeleton-line skeleton-w-70"></div></td>
              <td><div class="skeleton-line skeleton-w-50"></div></td>
              <td><div class="skeleton-line skeleton-w-30"></div></td>
              <td><div class="skeleton-line skeleton-w-30"></div></td>
              <td><div class="skeleton-line skeleton-w-30"></div></td>
              <td><div class="skeleton-line skeleton-w-30"></div></td>
              <td><div class="skeleton-line skeleton-w-60"></div></td>
            </tr>
          </template>
          <tr v-else v-for="item in paginatedMaterials" :key="item.id">
            <td><code>{{ getMaterialDisplayId(item) }}</code></td>
            <td><strong>{{ item.name }}</strong></td>
            <td>{{ item.category }}</td>
            <td>{{ item.total_quantity }}</td>
            <td>{{ item.available_quantity }}</td>
            <td>{{ (item.damaged_quantity || 0).toLocaleString() }}</td>
            <td>{{ (item.lost_quantity || 0).toLocaleString() }}</td>
            <td class="actions-cell">
              <div class="actions-dropdown">
                <button class="btn-icon details" title="Détails" @click.stop="toggleActions(item.id)">
                  <i class="fas fa-ellipsis-vertical"></i>
                </button>
                <div v-if="openActionsId === item.id" class="actions-menu" @click.stop>
                  <button class="actions-item" @click="openQtyModal(item, 'damaged')">
                    <i class="fas fa-tools"></i> Endommagé
                  </button>
                  <button class="actions-item" @click="openQtyModal(item, 'lost')">
                    <i class="fas fa-times-circle"></i> Perdu
                  </button>
                  <button class="actions-item" @click="viewMaterial(item)">
                    <i class="fas fa-eye"></i> Voir
                  </button>
                  <button class="actions-item" @click="editMaterial(item)">
                    <i class="fas fa-edit"></i> Modifier
                  </button>
                  <button class="actions-item danger" @click="confirmDelete(item)">
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
    <AdminAppModal v-model="showFormModal" :title="isEditing ? 'Modifier le matériel' : 'Ajouter du matériel'" width="500px">
      <form @submit.prevent="saveMaterial" class="admin-form">
        <div class="form-group">
          <label class="form-label">Nom de l'article</label>
          <input v-model="form.name" type="text" class="form-input" required placeholder="Ex: Chaises Napoléon" />
        </div>
        <div class="form-group">
          <label class="form-label">Catégorie</label>
          <select v-model="form.category" class="form-select" required>
            <option value="Mobilier">Mobilier</option>
            <option value="Audiovisuel">Audiovisuel</option>
            <option value="Linge">Linge</option>
            <option value="Décoration">Décoration</option>
            <option value="Cuisine">Cuisine</option>
          </select>
        </div>
        <div class="form-grid">
          <div class="form-group">
            <label class="form-label">Quantité Totale</label>
            <input v-model.number="form.total_quantity" type="number" class="form-input" required />
          </div>
          <div class="form-group">
            <label class="form-label">Quantité Disponible</label>
            <input :value="availablePreview" type="number" class="form-input" disabled />
          </div>
        </div>
        <div class="form-group" v-if="isEditing">
          <label class="form-label">Quantités (gestion)</label>
          <div class="qty-hint">
            <span>Endommagé: <strong>{{ (form.damaged_quantity || 0).toLocaleString() }}</strong></span>
            <span>Perdu: <strong>{{ (form.lost_quantity || 0).toLocaleString() }}</strong></span>
            <span class="hint">Utiliser les boutons Endommagé / Perdu dans la liste pour modifier.</span>
          </div>
        </div>
      </form>
      <template #footer>
        <button class="btn btn-outline" @click="showFormModal = false">Annuler</button>
        <button class="btn btn-primary" :class="{ 'is-loading': savingMaterial }" :disabled="savingMaterial" @click="saveMaterial">
          {{ isEditing ? 'Mettre à jour' : 'Ajouter' }}
        </button>
      </template>
    </AdminAppModal>

    <AdminAppModal v-model="showQtyModal" :title="qtyTitle" width="420px">
      <form class="admin-form" @submit.prevent="saveQty">
        <div v-if="qtyMaterial" class="qty-summary">
          <div><strong>Article:</strong> {{ qtyMaterial.name }}</div>
          <div><strong>Total:</strong> {{ qtyMaterial.total_quantity }}</div>
          <div><strong>En Stock:</strong> {{ qtyMaterial.available_quantity }}</div>
          <div><strong>Endommagé:</strong> {{ qtyMaterial.damaged_quantity || 0 }}</div>
          <div><strong>Perdu:</strong> {{ qtyMaterial.lost_quantity || 0 }}</div>
        </div>
        <div class="form-group">
          <label class="form-label">{{ qtyLabel }}</label>
          <input v-model.number="qtyValue" type="number" min="0" class="form-input" required />
          <small class="form-hint">La quantité disponible est recalculée automatiquement.</small>
        </div>
      </form>
      <template #footer>
        <button class="btn btn-outline" @click="showQtyModal = false">Annuler</button>
        <button class="btn btn-primary" :class="{ 'is-loading': savingQty }" :disabled="savingQty" @click="saveQty">
          Enregistrer
        </button>
      </template>
    </AdminAppModal>

    <!-- View Modal -->
    <AdminAppModal v-model="showViewModal" title="Détails du matériel" width="400px">
      <div v-if="selectedMaterial" class="view-details">
        <div class="detail-item">
          <span class="detail-label">ID</span>
          <span class="detail-val">{{ getMaterialDisplayId(selectedMaterial) }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">Nom</span>
          <span class="detail-val">{{ selectedMaterial.name }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">Catégorie</span>
          <span class="detail-val">{{ selectedMaterial.category }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">Quantité Totale</span>
          <span class="detail-val">{{ selectedMaterial.total_quantity }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">En Stock</span>
          <span class="detail-val">{{ selectedMaterial.available_quantity }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">Endommagé</span>
          <span class="detail-val">{{ selectedMaterial.damaged_quantity || 0 }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">Perdu</span>
          <span class="detail-val">{{ selectedMaterial.lost_quantity || 0 }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">Créé par</span>
          <span class="detail-val">{{ selectedMaterial.created_by_name || '-' }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">Dernière action par</span>
          <span class="detail-val">{{ selectedMaterial.updated_by_name || selectedMaterial.created_by_name || '-' }}</span>
        </div>
      </div>
      <template #footer>
        <button class="btn btn-primary" @click="showViewModal = false">Fermer</button>
      </template>
    </AdminAppModal>

    <!-- Delete Confirmation Modal -->
    <AdminAppModal v-model="showDeleteModal" title="Confirmer la suppression" width="400px">
      <p>Êtes-vous sûr de vouloir supprimer <strong>{{ selectedMaterial?.name }}</strong> ?</p>
      <template #footer>
        <button class="btn btn-outline" @click="showDeleteModal = false">Annuler</button>
        <button class="btn btn-danger" :class="{ 'is-loading': deletingMaterial }" :disabled="deletingMaterial" @click="deleteMaterial">
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

definePageMeta({ layout: 'admin' })
const route = useRoute()

const materials = ref([])
const { buildHashSequenceMap } = useDisplayIds()
const {
  sortedItems: sortedMaterials,
  toggleSort: toggleMaterialSort,
  isSortActive: isMaterialSortActive,
  sortIconClass: materialSortIconClass,
} = useTableSort(computed(() => materials.value), {
  initialKey: 'id',
  initialDirection: 'desc',
  accessors: {
    total_quantity: item => Number(item?.total_quantity || 0),
    available_quantity: item => Number(item?.available_quantity || 0),
    damaged_quantity: item => Number(item?.damaged_quantity || 0),
    lost_quantity: item => Number(item?.lost_quantity || 0),
  },
})
const {
  paginatedItems: paginatedMaterials,
  totalItems: materialsTotalItems,
  startIndex: materialsStartIndex,
  endIndex: materialsEndIndex,
  canPrev: materialsCanPrev,
  canNext: materialsCanNext,
  prevPage: materialsPrevPage,
  nextPage: materialsNextPage,
} = usePagination(sortedMaterials, 50)
const tableRef = ref(null)
const exportingPdf = ref(false)
const exportingXls = ref(false)
const loadingMaterials = ref(false)
const openActionsId = ref(null)
const isMobile = ref(false)
const savingMaterial = ref(false)
const savingQty = ref(false)
const deletingMaterial = ref(false)

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
  a.download = 'materials.xls'
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
  win.document.write(`<!doctype html><html><head><meta charset="utf-8"><title>Matériel</title><style>
  body{font-family:Arial, sans-serif; padding:20px}
  table{width:100%; border-collapse:collapse}
  th,td{border:1px solid #e2e8f0; padding:8px; text-align:left; font-size:12px}
  th{background:#f8fafc}
  </style></head><body><h2>Matériel</h2>${tableRef.value.outerHTML}</body></html>`)
  win.document.close()
  win.focus()
  win.print()
  win.close()
  setTimeout(() => {
    exportingPdf.value = false
  }, 350)
}
const showFormModal = ref(false)
const showQtyModal = ref(false)
const showViewModal = ref(false)
const showDeleteModal = ref(false)
const isEditing = ref(false)
const selectedMaterial = ref(null)
const qtyMaterial = ref(null)
const qtyMode = ref('damaged')
const qtyValue = ref(0)

const form = ref({
  id: null,
  name: '',
  category: 'Mobilier',
  total_quantity: 0,
  damaged_quantity: 0,
  lost_quantity: 0
})

const fetchMaterials = async () => {
  loadingMaterials.value = true
  try {
    const response = await api.get('materials/')
    materials.value = Array.isArray(response.data) ? response.data : []
  } catch (error) {
    notify('Erreur lors du chargement du matériel', 'danger')
  } finally {
    loadingMaterials.value = false
  }
}

const openMaterialFromQuery = () => {
  const viewId = Number(route.query.view)
  if (!viewId) return
  const material = materials.value.find(item => Number(item?.id) === viewId)
  if (!material) return
  selectedMaterial.value = material
  showViewModal.value = true
}

watch(() => `${route.query.view || ''}:${route.query.focus || ''}:${materials.value.length}`, () => {
  openMaterialFromQuery()
})

onMounted(async () => {
  await fetchMaterials()
  openMaterialFromQuery()
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

const resetForm = () => {
  form.value = {
    id: null,
    name: '',
    category: 'Mobilier',
    total_quantity: 0,
    damaged_quantity: 0,
    lost_quantity: 0
  }
}

const openAddModal = () => {
  isEditing.value = false
  resetForm()
  showFormModal.value = true
}

const viewMaterial = (item) => {
  closeActions()
  selectedMaterial.value = item
  showViewModal.value = true
}

const editMaterial = (item) => {
  closeActions()
  isEditing.value = true
  form.value = {
    id: item.id,
    name: item.name,
    category: item.category,
    total_quantity: item.total_quantity,
    damaged_quantity: item.damaged_quantity || 0,
    lost_quantity: item.lost_quantity || 0,
  }
  showFormModal.value = true
}

const confirmDelete = (item) => {
  closeActions()
  selectedMaterial.value = item
  showDeleteModal.value = true
}

const saveMaterial = async () => {
  if (savingMaterial.value) return
  savingMaterial.value = true
  try {
    if (isEditing.value) {
      await api.put(`materials/${form.value.id}/`, {
        id: form.value.id,
        name: form.value.name,
        category: form.value.category,
        total_quantity: form.value.total_quantity,
        damaged_quantity: form.value.damaged_quantity || 0,
        lost_quantity: form.value.lost_quantity || 0,
      })
      notify('Matériel mis à jour avec succès')
    } else {
      await api.post('materials/', {
        name: form.value.name,
        category: form.value.category,
        total_quantity: form.value.total_quantity,
      })
      notify('Nouveau matériel ajouté avec succès')
    }
    showFormModal.value = false
    fetchMaterials()
  } catch (error) {
    notify('Erreur lors de l\'enregistrement', 'danger')
  } finally {
    savingMaterial.value = false
  }
}

const deleteMaterial = async () => {
  if (deletingMaterial.value || !selectedMaterial.value?.id) return
  deletingMaterial.value = true
  try {
    await api.delete(`materials/${selectedMaterial.value.id}/`)
    notify('Matériel supprimé', 'danger')
    showDeleteModal.value = false
    fetchMaterials()
  } catch (error) {
    notify('Erreur lors de la suppression', 'danger')
  } finally {
    deletingMaterial.value = false
  }
}

const openQtyModal = (item, mode) => {
  closeActions()
  qtyMaterial.value = item
  qtyMode.value = mode
  qtyValue.value = mode === 'lost' ? Number(item.lost_quantity || 0) : Number(item.damaged_quantity || 0)
  showQtyModal.value = true
}

const qtyTitle = computed(() => qtyMode.value === 'lost' ? 'Modifier Perdu' : 'Modifier Endommagé')
const qtyLabel = computed(() => qtyMode.value === 'lost' ? 'Quantité perdue' : 'Quantité endommagée')
const materialDisplayIds = computed(() => buildHashSequenceMap(materials.value))
const getMaterialDisplayId = (item) => materialDisplayIds.value.get(item?.id) || '#0001'
const availablePreview = computed(() => {
  const total = Number(form.value.total_quantity || 0)
  const damaged = Number(form.value.damaged_quantity || 0)
  const lost = Number(form.value.lost_quantity || 0)
  return Math.max(0, total - damaged - lost)
})

const saveQty = async () => {
  if (!qtyMaterial.value) return
  if (savingQty.value) return
  savingQty.value = true
  try {
    const payload = qtyMode.value === 'lost'
      ? { lost_quantity: qtyValue.value }
      : { damaged_quantity: qtyValue.value }
    await api.patch(`materials/${qtyMaterial.value.id}/`, payload)
    notify('Quantité mise à jour', 'success')
    showQtyModal.value = false
    qtyMaterial.value = null
    fetchMaterials()
  } catch (error) {
    const msg = error?.response?.data?.non_field_errors?.[0] || 'Erreur lors de la mise à jour'
    notify(msg, 'danger')
  } finally {
    savingQty.value = false
  }
}

const totalAvailable = computed(() => (materials.value || []).reduce((a, m) => a + Number(m.available_quantity || 0), 0))
const totalDamaged = computed(() => (materials.value || []).reduce((a, m) => a + Number(m.damaged_quantity || 0), 0))
const totalLost = computed(() => (materials.value || []).reduce((a, m) => a + Number(m.lost_quantity || 0), 0))

const displayMaterialsCount = ref(0)
const displayTotalAvailable = ref(0)
const displayTotalDamaged = ref(0)
const displayTotalLost = ref(0)

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

watch(() => materials.value.length, (v) => animateCounter(displayMaterialsCount, v), { immediate: true })
watch(totalAvailable, (v) => animateCounter(displayTotalAvailable, v), { immediate: true })
watch(totalDamaged, (v) => animateCounter(displayTotalDamaged, v), { immediate: true })
watch(totalLost, (v) => animateCounter(displayTotalLost, v), { immediate: true })

onBeforeUnmount(() => {
  for (const id of rafMap.values()) cancelAnimationFrame(id)
})
</script>

<style scoped>
.admin-materials {
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

.header-actions h1 {
  font-size: 1.75rem;
  font-weight: 800;
  color: #0f172a;
  margin-bottom: 0;
}

.qty-summary {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: .85rem 1rem;
  display: grid;
  gap: .25rem;
  margin-bottom: .75rem;
  color: #0f172a;
  font-weight: 650;
}

.qty-hint {
  display: grid;
  gap: .35rem;
  padding: .75rem 1rem;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  background: #f8fafc;
  color: #0f172a;
  font-weight: 650;
}

.qty-hint .hint {
  color: #94a3b8;
  font-weight: 600;
  font-size: 0.85rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
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
.stat-icon.info { background: #f0f9ff; color: #0ea5e9; }
.stat-icon.success { background: #f0fdf4; color: #22c55e; }
.stat-icon.warning { background: #fffbeb; color: #f59e0b; }
.stat-icon.danger { background: #fef2f2; color: #ef4444; }

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-label {
  font-size: 0.7rem;
  color: #94a3b8;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.125rem;
}

.stat-value {
  font-size: 1.25rem;
  font-weight: 800;
  color: #0f172a;
  line-height: 1.2;
}

.value.success { color: #22c55e; }
.value.warning { color: #f59e0b; }
.value.danger { color: #ef4444; }

.btn-icon {
  width: 34px;
  height: 34px;
  background: #f8fafc;
  color: #94a3b8;
}

.btn-icon:hover {
  background: #f1f5f9;
}

.btn-icon.warning:hover { color: var(--warning); }
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

.actions-item.danger {
  color: #dc2626;
}

.actions-item.danger:hover {
  background: #fef2f2;
  color: #b91c1c;
}
</style>
